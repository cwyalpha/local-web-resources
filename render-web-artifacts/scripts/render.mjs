#!/usr/bin/env node

import { createReadStream, existsSync, statSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.dirname(SCRIPT_DIR);
const ASSETS_DIR = path.join(SKILL_DIR, "assets");
const DYNAMIC_PATH = "/__render_document__.html";
const MAX_FULL_PAGE_HEIGHT = 30_000;
const MIME_TYPES = new Map([
  [".html", "text/html; charset=utf-8"],
  [".htm", "text/html; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".mjs", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".gif", "image/gif"],
  [".webp", "image/webp"],
  [".ico", "image/x-icon"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
  [".ttf", "font/ttf"],
  [".otf", "font/otf"],
  [".wasm", "application/wasm"],
  [".pdf", "application/pdf"],
  [".map", "application/json; charset=utf-8"],
]);

const HELP = `Usage:
  node scripts/render.mjs <html|markdown|mermaid|echarts>
    --input <file|URL|-> --output <file>

Options:
  --width <px>          Viewport/chart width
  --height <px>         Viewport/chart height
  --selector <css>      Capture exactly one HTML element (PNG/JPEG only)
  --full-page           Capture the full HTML/Markdown page
  --wait-selector <css> Wait for a visible element
  --wait-ms <ms>        Extra settling time (default: 500)
  --timeout <ms>        Navigation/readiness timeout (default: 30000)
  --paper <name>        A3, A4, A5, Letter, Legal, or Tabloid
  --landscape           Landscape PDF
  --theme <light|dark>  Color theme
  --strict              Fail on resource and console errors
  --keep-animations     Do not disable/finish animations
  --help                Show this help
`;

function fail(message) {
  throw new Error(message);
}

function parseInteger(raw, fallback, name, minimum, maximum) {
  if (raw === undefined) return fallback;
  if (!/^\d+$/.test(raw)) fail(`--${name} must be an integer`);
  const value = Number(raw);
  if (value < minimum || value > maximum) {
    fail(`--${name} must be between ${minimum} and ${maximum}`);
  }
  return value;
}

function parseArgs(argv) {
  if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
    return { help: true };
  }

  const command = argv[0];
  if (!["html", "markdown", "mermaid", "echarts"].includes(command)) {
    fail(`Unknown command: ${command}`);
  }

  const booleanFlags = new Set([
    "full-page",
    "landscape",
    "strict",
    "keep-animations",
  ]);
  const values = {};
  for (let index = 1; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) fail(`Unexpected argument: ${token}`);
    const key = token.slice(2);
    if (booleanFlags.has(key)) {
      values[key] = true;
      continue;
    }
    const value = argv[index + 1];
    if (value === undefined || value.startsWith("--")) {
      fail(`Missing value for --${key}`);
    }
    values[key] = value;
    index += 1;
  }

  const allowed = new Set([
    "input",
    "output",
    "width",
    "height",
    "selector",
    "full-page",
    "wait-selector",
    "wait-ms",
    "timeout",
    "paper",
    "landscape",
    "theme",
    "strict",
    "keep-animations",
  ]);
  for (const key of Object.keys(values)) {
    if (!allowed.has(key)) fail(`Unknown option: --${key}`);
  }
  if (!values.output) fail("--output is required");

  const chartCommand = command === "mermaid" || command === "echarts";
  const width = parseInteger(values.width, chartCommand ? 1200 : 1440, "width", 200, 10_000);
  const height = parseInteger(values.height, chartCommand ? 675 : 900, "height", 200, 10_000);
  const waitMs = parseInteger(values["wait-ms"], 500, "wait-ms", 0, 30_000);
  const timeout = parseInteger(values.timeout, 30_000, "timeout", 1_000, 120_000);
  const theme = values.theme ?? "light";
  if (!["light", "dark"].includes(theme)) fail("--theme must be light or dark");

  const paper = values.paper ?? "A4";
  const papers = new Map([
    ["a3", "A3"],
    ["a4", "A4"],
    ["a5", "A5"],
    ["letter", "Letter"],
    ["legal", "Legal"],
    ["tabloid", "Tabloid"],
  ]);
  const normalizedPaper = papers.get(paper.toLowerCase());
  if (!normalizedPaper) {
    fail("--paper must be A3, A4, A5, Letter, Legal, or Tabloid");
  }

  return {
    help: false,
    command,
    input: values.input ?? "-",
    output: path.resolve(values.output),
    width,
    height,
    selector: values.selector,
    fullPage: Boolean(values["full-page"]),
    waitSelector: values["wait-selector"],
    waitMs,
    timeout,
    paper: normalizedPaper,
    landscape: Boolean(values.landscape),
    theme,
    strict: Boolean(values.strict),
    keepAnimations: Boolean(values["keep-animations"]),
  };
}

function outputFormat(filename) {
  const extension = path.extname(filename).toLowerCase();
  const formats = new Map([
    [".png", "png"],
    [".jpg", "jpeg"],
    [".jpeg", "jpeg"],
    [".pdf", "pdf"],
    [".svg", "svg"],
  ]);
  const format = formats.get(extension);
  if (!format) fail(`Unsupported output extension: ${extension || "(none)"}`);
  return format;
}

function validateFormat(command, format, selector) {
  const allowed = {
    html: new Set(["png", "jpeg", "pdf"]),
    markdown: new Set(["png", "jpeg", "pdf"]),
    mermaid: new Set(["png", "svg", "pdf"]),
    echarts: new Set(["png", "svg", "pdf"]),
  };
  if (!allowed[command].has(format)) {
    fail(`${command} does not support ${format} output`);
  }
  if (selector && format === "pdf") {
    fail("--selector only supports PNG/JPEG; choose a full page PDF or an image output");
  }
  if (selector && command !== "html") {
    fail("--selector is only valid with the html command");
  }
}

function isHttpUrl(value) {
  return /^https?:\/\//i.test(value);
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

async function readTextInput(input, timeout) {
  if (input === "-") return readStdin();
  if (isHttpUrl(input)) {
    const response = await fetch(input, { signal: AbortSignal.timeout(timeout) });
    if (!response.ok) {
      fail(`Failed to download input: HTTP ${response.status} ${input}`);
    }
    return response.text();
  }
  return readFile(path.resolve(input), "utf8");
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("'", "&#39;");
}

function resolveLocalInput(input) {
  const absolute = path.resolve(input);
  if (!existsSync(absolute) || !statSync(absolute).isFile()) {
    fail(`Input file does not exist: ${absolute}`);
  }
  return absolute;
}

async function runProcess(command, args, stdinText, timeout) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: ["pipe", "pipe", "pipe"] });
    const stdout = [];
    const stderr = [];
    let settled = false;
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
      reject(new Error(`${command} timed out after ${timeout}ms`));
    }, timeout);

    child.stdout.on("data", (chunk) => stdout.push(chunk));
    child.stderr.on("data", (chunk) => stderr.push(chunk));
    child.on("error", (error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(error);
    });
    child.on("close", (code) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      const out = Buffer.concat(stdout).toString("utf8");
      const err = Buffer.concat(stderr).toString("utf8");
      if (code !== 0) reject(new Error(`${command} failed (${code}): ${err.trim()}`));
      else resolve(out);
    });
    child.stdin.end(stdinText);
  });
}

async function markdownToHtml(markdown, options, input) {
  const body = await runProcess(
    "pandoc",
    ["--from=gfm+raw_html", "--to=html5"],
    markdown,
    options.timeout,
  );
  const template = await readFile(path.join(ASSETS_DIR, "markdown-template.html"), "utf8");
  const style = await readFile(path.join(ASSETS_DIR, "print.css"), "utf8");
  const title = input !== "-" && !isHttpUrl(input)
    ? path.basename(input, path.extname(input))
    : "Markdown Document";
  const baseHref = isHttpUrl(input) ? new URL(".", input).href : "/";

  return template
    .replace("{{THEME}}", escapeAttribute(options.theme))
    .replace("{{BASE_HREF}}", escapeAttribute(baseHref))
    .replace("{{TITLE}}", escapeHtml(title))
    .replace("{{STYLE}}", style)
    .replace("{{BODY}}", body);
}

function chartHtml(kind, content, options) {
  const background = options.theme === "dark" ? "#18212f" : "#ffffff";
  const foreground = options.theme === "dark" ? "#e5e7eb" : "#1f2937";
  const inner = kind === "mermaid"
    ? `<div id="artifact" class="mermaid">${escapeHtml(content)}</div>`
    : '<div id="artifact"></div>';
  return `<!doctype html>
<html lang="zh-CN" data-theme="${options.theme}">
<head>
  <meta charset="utf-8">
  <style>
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 100%; min-height: 100%; background: ${background}; color: ${foreground}; }
    body { font-family: "Noto Sans CJK SC", "Noto Sans SC", "Microsoft YaHei", sans-serif; }
    #artifact { width: ${options.width}px; height: ${options.height}px; background: ${background}; }
    #artifact.mermaid { height: auto; min-height: 1px; display: inline-block; }
    #artifact.mermaid svg { display: block; max-width: none !important; }
  </style>
</head>
<body>${inner}</body>
</html>`;
}

function createStaticServer(root, dynamicHtml) {
  const resolvedRoot = path.resolve(root);
  const rootPrefix = resolvedRoot.endsWith(path.sep) ? resolvedRoot : `${resolvedRoot}${path.sep}`;
  const server = http.createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url ?? "/", "http://127.0.0.1");
      if (requestUrl.pathname === DYNAMIC_PATH && dynamicHtml !== undefined) {
        response.writeHead(200, {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-store",
        });
        response.end(request.method === "HEAD" ? undefined : dynamicHtml);
        return;
      }

      let decoded;
      try {
        decoded = decodeURIComponent(requestUrl.pathname);
      } catch {
        response.writeHead(400);
        response.end("Bad request");
        return;
      }
      let candidate = path.resolve(resolvedRoot, `.${decoded}`);
      if (candidate !== resolvedRoot && !candidate.startsWith(rootPrefix)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
      }
      if (existsSync(candidate) && statSync(candidate).isDirectory()) {
        candidate = path.join(candidate, "index.html");
      }
      if (!existsSync(candidate) || !statSync(candidate).isFile()) {
        response.writeHead(404);
        response.end("Not found");
        return;
      }

      const contentType = MIME_TYPES.get(path.extname(candidate).toLowerCase())
        ?? "application/octet-stream";
      response.writeHead(200, {
        "Content-Type": contentType,
        "Cache-Control": "no-store",
      });
      if (request.method === "HEAD") response.end();
      else createReadStream(candidate).pipe(response);
    } catch (error) {
      response.writeHead(500);
      response.end(error.message);
    }
  });

  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      resolve({ server, origin: `http://127.0.0.1:${address.port}` });
    });
  });
}

async function closeServer(server) {
  if (!server) return;
  await new Promise((resolve) => server.close(resolve));
}

function loadPlaywright() {
  try {
    return require("playwright");
  } catch (error) {
    fail(`Playwright is unavailable. Use the Docker image or install the pinned dependency. ${error.message}`);
  }
}

function resolveEchartsBundle() {
  for (const candidate of [
    "echarts/dist/echarts.min.js",
    "echarts/dist/echarts.js",
    "echarts",
  ]) {
    try {
      return require.resolve(candidate);
    } catch {
      // Try the next known package entry.
    }
  }
  fail("Cannot resolve the shared ECharts browser bundle");
}

async function injectAnimationPolicy(page, keepAnimations) {
  if (keepAnimations) return;
  await page.addStyleTag({
    content: `*, *::before, *::after {
      animation-duration: 0s !important;
      animation-delay: 0s !important;
      transition-duration: 0s !important;
      transition-delay: 0s !important;
      caret-color: transparent !important;
    }`,
  });
}

async function enhanceMarkdownCharts(page, options, format) {
  const chartKinds = await page.evaluate(() => {
    const result = { mermaid: 0, echarts: 0 };
    for (const code of document.querySelectorAll("pre > code")) {
      const pre = code.parentElement;
      const isMermaid = code.classList.contains("language-mermaid")
        || pre.classList.contains("mermaid");
      const isEcharts = code.classList.contains("language-echarts")
        || pre.classList.contains("echarts");
      if (!isMermaid && !isEcharts) continue;
      const replacement = document.createElement("div");
      replacement.className = isMermaid ? "mermaid" : "echarts-artifact";
      replacement.dataset.source = code.textContent ?? "";
      code.parentElement.replaceWith(replacement);
      result[isMermaid ? "mermaid" : "echarts"] += 1;
    }
    return result;
  });

  if (chartKinds.mermaid > 0) {
    await page.addScriptTag({ path: path.join(ASSETS_DIR, "mermaid.min.js") });
    await page.evaluate(
      async ({ theme }) => {
        window.mermaid.initialize({
          startOnLoad: false,
          securityLevel: "loose",
          theme: theme === "dark" ? "dark" : "default",
          deterministicIds: true,
          deterministicIDSeed: "render-web-artifacts",
          flowchart: { htmlLabels: true },
        });
        for (const node of document.querySelectorAll(".mermaid")) {
          node.textContent = node.dataset.source ?? "";
          delete node.dataset.source;
        }
        await window.mermaid.run({ nodes: [...document.querySelectorAll(".mermaid")] });
      },
      { theme: options.theme },
    );
  }

  if (chartKinds.echarts > 0) {
    await page.addScriptTag({ path: resolveEchartsBundle() });
    await page.evaluate(
      ({ theme, keepAnimations, renderer }) => {
        for (const node of document.querySelectorAll(".echarts-artifact")) {
          let option;
          try {
            option = JSON.parse(node.dataset.source ?? "");
          } catch (error) {
            throw new Error(`Invalid ECharts JSON in Markdown: ${error.message}`);
          }
          delete node.dataset.source;
          if (!keepAnimations) {
            option.animation = false;
            for (const series of Array.isArray(option.series) ? option.series : []) {
              series.animation = false;
            }
          }
          const chart = window.echarts.init(
            node,
            theme === "dark" ? "dark" : null,
            { renderer },
          );
          chart.setOption(option, { notMerge: true, lazyUpdate: false });
          chart.resize();
        }
      },
      {
        theme: options.theme,
        keepAnimations: options.keepAnimations,
        renderer: format === "pdf" ? "svg" : "canvas",
      },
    );
  }
}

async function waitForPageReady(page, options) {
  if (options.waitSelector) {
    await page.locator(options.waitSelector).first().waitFor({
      state: "visible",
      timeout: options.timeout,
    });
  }

  await page.waitForLoadState("load", { timeout: options.timeout });
  await page.waitForLoadState("networkidle", {
    timeout: Math.min(options.timeout, 3_000),
  }).catch(() => {});

  await page.evaluate(async (timeout) => {
    const waitForImages = Promise.all(
      [...document.images]
        .filter((image) => !image.complete)
        .map((image) => new Promise((resolve) => {
          image.addEventListener("load", resolve, { once: true });
          image.addEventListener("error", resolve, { once: true });
        })),
    );
    const waitForFonts = document.fonts?.ready ?? Promise.resolve();
    await Promise.race([
      Promise.all([waitForImages, waitForFonts]),
      new Promise((_, reject) => setTimeout(
        () => reject(new Error("Timed out waiting for images or fonts")),
        timeout,
      )),
    ]);
  }, options.timeout);

  const readyState = await page.evaluate(() => ({
    hasGlobal: Object.prototype.hasOwnProperty.call(window, "__RENDER_READY__"),
    attribute: document.documentElement.getAttribute("data-render-ready"),
  }));
  if (readyState.hasGlobal || readyState.attribute !== null) {
    await page.waitForFunction(
      () => window.__RENDER_READY__ === true
        || document.documentElement.getAttribute("data-render-ready") === "true",
      undefined,
      { timeout: options.timeout },
    );
  }

  if (!options.keepAnimations) {
    await page.evaluate(() => {
      if (!window.echarts) return;
      for (const node of document.querySelectorAll("[_echarts_instance_]")) {
        const chart = window.echarts.getInstanceByDom(node);
        if (!chart) continue;
        chart.getZr()?.animation?.stop();
        chart.resize();
      }
    });
  }

  if (options.waitMs > 0) await page.waitForTimeout(options.waitMs);
  await page.evaluate(() => new Promise((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  }));
}

async function uniqueVisibleLocator(page, selector, timeout) {
  const locator = page.locator(selector);
  const count = await locator.count();
  if (count !== 1) {
    fail(`--selector must match exactly one element; matched ${count}: ${selector}`);
  }
  await locator.waitFor({ state: "visible", timeout });
  await locator.scrollIntoViewIfNeeded({ timeout });
  await waitForStableElement(locator, timeout);
  return locator;
}

async function waitForStableElement(locator, timeout) {
  const deadline = Date.now() + timeout;
  let previous;
  let stableCount = 0;
  while (Date.now() < deadline) {
    const box = await locator.boundingBox();
    if (!box || box.width <= 0 || box.height <= 0) {
      fail("Selected element has no visible bounds");
    }
    const stable = previous
      && ["x", "y", "width", "height"].every(
        (key) => Math.abs(previous[key] - box[key]) < 0.5,
      );
    stableCount = stable ? stableCount + 1 : 0;
    if (stableCount >= 2) return box;
    previous = box;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  fail("Selected element did not reach a stable size before timeout");
}

async function assertFullPageHeight(page) {
  const dimensions = await page.evaluate(() => ({
    width: Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth ?? 0),
    height: Math.max(document.documentElement.scrollHeight, document.body?.scrollHeight ?? 0),
  }));
  if (dimensions.height > MAX_FULL_PAGE_HEIGHT) {
    fail(`Full page height ${dimensions.height}px exceeds ${MAX_FULL_PAGE_HEIGHT}px; use PDF or split the page`);
  }
  return dimensions;
}

async function screenshot(page, locator, options, format, fullPage) {
  const screenshotOptions = {
    path: options.output,
    type: format,
    animations: options.keepAnimations ? "allow" : "disabled",
    caret: "hide",
  };
  if (format === "jpeg") screenshotOptions.quality = 90;
  if (locator) {
    await locator.screenshot(screenshotOptions);
  } else {
    if (fullPage) await assertFullPageHeight(page);
    await page.screenshot({ ...screenshotOptions, fullPage });
  }
}

async function documentPdf(page, options) {
  await page.emulateMedia({ media: "print", colorScheme: options.theme });
  await page.pdf({
    path: options.output,
    format: options.paper,
    landscape: options.landscape,
    printBackground: true,
    preferCSSPageSize: false,
    margin: { top: "15mm", right: "15mm", bottom: "15mm", left: "15mm" },
  });
}

async function chartPdf(page, locator, options) {
  const box = await waitForStableElement(locator, options.timeout);
  await page.emulateMedia({ media: "print", colorScheme: options.theme });
  await page.pdf({
    path: options.output,
    width: `${Math.ceil(box.width)}px`,
    height: `${Math.ceil(box.height)}px`,
    printBackground: true,
    pageRanges: "1",
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
  });
}

async function render() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    process.stdout.write(HELP);
    return;
  }

  const startedAt = Date.now();
  const format = outputFormat(options.output);
  validateFormat(options.command, format, options.selector);
  await mkdir(path.dirname(options.output), { recursive: true });

  let browser;
  let server;
  const resourceWarnings = [];
  const consoleErrors = [];
  const pageErrors = [];

  try {
    let targetUrl;
    let dynamicHtml;
    let serverRoot = process.cwd();
    let sourceText;

    if (options.command === "html") {
      if (isHttpUrl(options.input)) {
        targetUrl = options.input;
      } else if (options.input === "-") {
        dynamicHtml = await readStdin();
      } else {
        const inputPath = resolveLocalInput(options.input);
        serverRoot = path.dirname(inputPath);
        targetUrl = `LOCAL:${encodeURIComponent(path.basename(inputPath))}`;
      }
    } else {
      sourceText = await readTextInput(options.input, options.timeout);
      if (options.command === "markdown") {
        dynamicHtml = await markdownToHtml(sourceText, options, options.input);
        if (options.input !== "-" && !isHttpUrl(options.input)) {
          serverRoot = path.dirname(resolveLocalInput(options.input));
        }
      } else {
        dynamicHtml = chartHtml(options.command, sourceText, options);
      }
    }

    if (!targetUrl || targetUrl.startsWith("LOCAL:")) {
      const localName = targetUrl?.slice("LOCAL:".length);
      const opened = await createStaticServer(serverRoot, dynamicHtml);
      server = opened.server;
      targetUrl = localName
        ? `${opened.origin}/${localName}`
        : `${opened.origin}${DYNAMIC_PATH}`;
    }

    const { chromium } = loadPlaywright();
    browser = await chromium.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });
    const context = await browser.newContext({
      viewport: { width: options.width, height: options.height },
      deviceScaleFactor: 2,
      locale: "zh-CN",
      timezoneId: "Asia/Shanghai",
      colorScheme: options.theme,
    });
    const page = await context.newPage();
    page.setDefaultTimeout(options.timeout);
    page.setDefaultNavigationTimeout(options.timeout);

    page.on("requestfailed", (request) => {
      resourceWarnings.push({
        type: "requestfailed",
        url: request.url(),
        detail: request.failure()?.errorText ?? "unknown",
      });
    });
    page.on("response", (response) => {
      if (response.status() >= 400) {
        resourceWarnings.push({
          type: "http",
          url: response.url(),
          detail: String(response.status()),
        });
      }
    });
    page.on("pageerror", (error) => pageErrors.push(error.message));
    page.on("console", (message) => {
      if (message.type() === "error") consoleErrors.push(message.text());
    });

    await page.goto(targetUrl, { waitUntil: "load", timeout: options.timeout });
    await injectAnimationPolicy(page, options.keepAnimations);

    let generatedLocator;
    if (options.command === "markdown") {
      await enhanceMarkdownCharts(page, options, format);
    } else if (options.command === "mermaid") {
      await page.addScriptTag({ path: path.join(ASSETS_DIR, "mermaid.min.js") });
      await page.evaluate(
        async ({ theme }) => {
          window.mermaid.initialize({
            startOnLoad: false,
            securityLevel: "loose",
            theme: theme === "dark" ? "dark" : "default",
            deterministicIds: true,
            deterministicIDSeed: "render-web-artifacts",
            flowchart: { htmlLabels: true },
          });
          await window.mermaid.run({ nodes: [document.querySelector("#artifact")] });
        },
        { theme: options.theme },
      );
      generatedLocator = await uniqueVisibleLocator(page, "#artifact svg", options.timeout);
    } else if (options.command === "echarts") {
      let option;
      try {
        option = JSON.parse(sourceText);
      } catch (error) {
        fail(`Invalid ECharts option JSON: ${error.message}`);
      }
      await page.addScriptTag({ path: resolveEchartsBundle() });
      await page.evaluate(
        ({ option: inputOption, theme, keepAnimations, renderer }) => {
          if (!keepAnimations) {
            inputOption.animation = false;
            for (const series of Array.isArray(inputOption.series) ? inputOption.series : []) {
              series.animation = false;
            }
          }
          const chart = window.echarts.init(
            document.querySelector("#artifact"),
            theme === "dark" ? "dark" : null,
            { renderer },
          );
          chart.setOption(inputOption, { notMerge: true, lazyUpdate: false });
          chart.resize();
        },
        {
          option,
          theme: options.theme,
          keepAnimations: options.keepAnimations,
          renderer: format === "png" ? "canvas" : "svg",
        },
      );
      generatedLocator = await uniqueVisibleLocator(page, "#artifact", options.timeout);
    }

    await waitForPageReady(page, options);
    if (pageErrors.length > 0) fail(`Page script error: ${pageErrors.join(" | ")}`);
    if (options.strict && (resourceWarnings.length > 0 || consoleErrors.length > 0)) {
      fail(
        `Strict mode failed: ${resourceWarnings.length} resource warning(s), `
        + `${consoleErrors.length} console error(s)`,
      );
    }

    if (options.command === "mermaid" || options.command === "echarts") {
      if (format === "svg") {
        const svg = await page.locator("#artifact svg").first().evaluate((node) => {
          if (!node.hasAttribute("xmlns")) {
            node.setAttribute("xmlns", "http://www.w3.org/2000/svg");
          }
          return node.outerHTML;
        });
        await writeFile(options.output, svg, "utf8");
      } else if (format === "pdf") {
        await chartPdf(page, generatedLocator, options);
      } else {
        await screenshot(page, generatedLocator, options, format, false);
      }
    } else if (format === "pdf") {
      await documentPdf(page, options);
    } else {
      const locator = options.selector
        ? await uniqueVisibleLocator(page, options.selector, options.timeout)
        : undefined;
      await screenshot(page, locator, options, format, !options.selector);
    }

    for (const warning of resourceWarnings) {
      process.stderr.write(`[resource warning] ${warning.type} ${warning.detail} ${warning.url}\n`);
    }
    for (const message of consoleErrors) {
      process.stderr.write(`[console error] ${message}\n`);
    }

    const stats = statSync(options.output);
    if (!stats.isFile() || stats.size === 0) fail(`Output is empty: ${options.output}`);
    process.stdout.write(`${JSON.stringify({
      ok: true,
      command: options.command,
      input: options.input,
      output: options.output,
      format,
      width: options.width,
      height: options.height,
      selector: options.selector ?? null,
      fullPage: (options.command === "html" || options.command === "markdown")
        && !options.selector
        && format !== "pdf",
      bytes: stats.size,
      resourceWarnings: resourceWarnings.length,
      consoleErrors: consoleErrors.length,
      elapsedMs: Date.now() - startedAt,
    })}\n`);
  } finally {
    if (browser) await browser.close().catch(() => {});
    await closeServer(server).catch(() => {});
  }
}

render().catch((error) => {
  process.stderr.write(`${JSON.stringify({ ok: false, error: error.message })}\n`);
  process.exitCode = 1;
});
