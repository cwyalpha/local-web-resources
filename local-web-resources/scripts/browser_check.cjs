/* Run with Node + playwright available in NODE_PATH; dependencies are maintenance-only. */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {chromium}=require('playwright');
const args=process.argv.slice(2),arg=(k,f)=>args.includes(k)?args[args.indexOf(k)+1]:f;
const root=path.resolve(arg('--server-dir',path.join(__dirname,'../../web-resources-server')));
const output=path.resolve(arg('--output',path.join(__dirname,'../../reports/browser')));
fs.mkdirSync(output,{recursive:true});
const types={'.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json','.svg':'image/svg+xml','.woff':'font/woff','.woff2':'font/woff2','.ttf':'font/ttf','.png':'image/png','.gif':'image/gif','.eot':'application/vnd.ms-fontobject'};
let base;
const server=http.createServer((req,res)=>{
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  res.setHeader('Access-Control-Allow-Origin','*');res.setHeader('X-Content-Type-Options','nosniff');
  if(pathname==='/__test'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<!doctype html><html><head><meta charset="utf-8"></head><body><div id="target" style="width:900px;height:400px"></div></body></html>');return;}
  if(!pathname.startsWith('/resources/')){res.writeHead(404);res.end();return;}
  const p=path.resolve(root,pathname.slice('/resources/'.length));
  if(!p.startsWith(root+path.sep)||!fs.existsSync(p)||!fs.statSync(p).isFile()){res.writeHead(404);res.end();return;}
  res.setHeader('Content-Type',(types[path.extname(p)]||'application/octet-stream')+(path.extname(p)==='.html'?'; charset=utf-8':''));
  if(p.endsWith('.html'))res.end(fs.readFileSync(p,'utf8').replaceAll('{BASE_URL}',base));else fs.createReadStream(p).pipe(res);
});
const filter=arg('--filter','');
const checks=filter&&fs.existsSync(path.join(output,'results.json'))?JSON.parse(fs.readFileSync(path.join(output,'results.json'),'utf8')):[];let browser;
async function run(name,work,viewport){
 if(filter&&!new RegExp(filter).test(name))return;
 const previous=checks.findIndex(c=>c.name===name);if(previous>=0)checks.splice(previous,1);
 const context=await browser.newContext({viewport:viewport||{width:1366,height:768},acceptDownloads:true});
 context.setDefaultTimeout(15000);
 console.log('START',name);
 const page=await context.newPage(),errors=[],requests=[];
 await context.route('**/*',route=>{const u=new URL(route.request().url());if(['data:','blob:','about:'].includes(u.protocol)||u.origin===new URL(base).origin)route.continue();else{errors.push('external request: '+u.href);route.abort();}});
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push('HTTP '+r.status()+' '+r.url());requests.push(r.url());});
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 try{const detail=await work(page,context);if(errors.length)throw Error(errors.join('\n'));checks.push({name,passed:true,detail,requests:requests.length});console.log('PASS',name);}
 catch(e){checks.push({name,passed:false,error:e.message,errors});console.log('FAIL',name,e.message.slice(0,350));await page.screenshot({path:path.join(output,name.replace(/[^a-z0-9_-]/ig,'_')+'-failure.png')}).catch(()=>{});}
 finally{await context.close();fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(checks,null,2));}
}
async function functional(page,name){return page.evaluate(async name=>{
 const target=document.getElementById('target'),assert=(v,msg)=>{if(!v)throw Error(msg)};
 switch(name){
 case 'arquero':{const rows=aq.from([{g:'a',v:2},{g:'a',v:4},{g:'b',v:9}]).groupby('g').rollup({total:d=>aq.op.sum(d.v)}).objects();assert(rows.find(r=>r.g==='a').total===6&&rows.length===2,'group totals');break;}
 case 'simple-statistics':assert(ss.median([1,2,3,4])===2.5&&Math.abs(ss.sampleStandardDeviation([1,2,3])-1)<1e-10,'statistics');break;
 case 'phosphor-icons':{for(const [cls,family] of [['ph','Phosphor'],['ph-thin','Phosphor-Thin'],['ph-light','Phosphor-Light'],['ph-bold','Phosphor-Bold'],['ph-fill','Phosphor-Fill'],['ph-duotone','Phosphor-Duotone']]){const el=document.createElement('i');el.className=cls+' ph-heart';target.append(el);const style=getComputedStyle(el,'::before');assert(style.content!=='none'&&style.content!=='normal','icon glyph '+cls);const faces=await document.fonts.load('32px "'+family+'"',style.content.replaceAll('"',''));assert(faces.length>0&&faces.every(f=>f.status==='loaded'),'icon font '+family);}break;}
 case 'bootstrap':{target.innerHTML='<div class="modal"><div class="modal-dialog"><div class="modal-content">test</div></div></div>';let m=new bootstrap.Modal(target.firstChild);m.show();assert(target.firstChild.classList.contains('show'),'modal');m.hide();m.dispose();break;}
 case 'alpinejs':{let el=document.createElement('div');el.setAttribute('x-data','{count: 2}');el.innerHTML='<span x-text="count"></span>';target.append(el);await new Promise(r=>setTimeout(r,100));assert(el.textContent==='2','Alpine state');break;}
 case 'lucide':target.innerHTML='<i data-lucide="qr-code"></i>';lucide.createIcons();assert(target.querySelector('svg'),'Lucide svg');break;
 case 'echarts':{let c=echarts.init(target);c.setOption({animation:false,xAxis:{data:['A','B']},yAxis:{},series:[{type:'bar',data:[1,2]}]});assert(c.getOption().series[0].data[1]===2,'chart data');assert(echarts.getMap('china'),'china map');c.setOption({series:[{type:'map',map:'china',data:[{name:'北京',value:10}]}]},true);break;}
 case 'Chart.js':{let canvas=document.createElement('canvas');target.append(canvas);new Chart(canvas,{type:'bar',data:{labels:['A'],datasets:[{data:[2]}]},options:{animation:false}});break;}
 case 'mermaid':{mermaid.initialize({startOnLoad:false});let result=await mermaid.render('graph','graph LR; A-->B');assert(result.svg.includes('<svg'),'Mermaid render');target.innerHTML=result.svg;break;}
 case 'tabulator-tables':{const table=new Tabulator(target,{data:[{id:1,name:'甲'},{id:2,name:'乙'}],columns:[{title:'姓名',field:'name'}]});await new Promise(r=>table.on('tableBuilt',r));table.setFilter('name','=','乙');assert(table.getData('active').length===1,'table filter');break;}
 case 'datatables':{target.innerHTML='<table><thead><tr><th>name</th></tr></thead><tbody><tr><td>A</td></tr><tr><td>B</td></tr></tbody></table>';let t=new DataTable(target.firstChild);t.search('B').draw();assert(t.rows({search:'applied'}).count()===1,'DataTables search');break;}
 case 'choices.js':{target.innerHTML='<select><option value="a">甲</option><option value="b">乙</option></select>';let c=new Choices(target.firstChild,{allowHTML:false});c.setChoiceByValue('b');assert(c.getValue(true)==='b','choice selection');break;}
 case 'dompurify':assert(!DOMPurify.sanitize('<img src=x onerror="alert(1)"><script>bad</script>').includes('onerror'),'sanitize');break;
 case 'marked':{let html=await marked.parse('# Title');assert(html.includes('<h1>'),'marked');break;}
 case 'markdown-it':assert(markdownit().render('# Title').includes('<h1>'),'markdown-it');break;
 case 'katex':katex.render('x^2+y^2',target);assert(target.querySelector('.katex'),'KaTeX');break;
 case 'xlsx':{let wb=XLSX.utils.book_new();XLSX.utils.book_append_sheet(wb,XLSX.utils.aoa_to_sheet([['中文',2]]),'Sheet1');let b=XLSX.write(wb,{type:'array',bookType:'xlsx'});let again=XLSX.read(b);assert(again.Sheets.Sheet1.A1.v==='中文','XLSX roundtrip');break;}
 case 'PapaParse':{let csv=Papa.unparse([{name:'中文',v:2}]);assert(Papa.parse(csv,{header:true}).data[0].name==='中文','CSV roundtrip');break;}
 case 'dayjs':assert(dayjs('2026-10-10').format('YYYY/MM/DD')==='2026/10/10','dayjs');break;
 case 'lodash.js':assert(_.uniq([1,1,2]).length===2,'lodash');break;
 case 'fuse.js':assert(new Fuse(['apple','banana']).search('appl')[0].item==='apple','Fuse');break;
 case 'countup.js':{target.innerHTML='<span id="count"></span>';let c=new countUp.CountUp('count',12,{duration:0});c.start();assert(!c.error,'countup');break;}
 case 'vue':Vue.createApp({data:()=>({msg:'中文'}),template:'<p>{{msg}}</p>'}).mount(target);await Vue.nextTick();assert(target.textContent==='中文','Vue');break;
 case 'cytoscape':{let cy=cytoscape({headless:true,elements:[{data:{id:'a'}},{data:{id:'b'}},{data:{id:'ab',source:'a',target:'b'}}]});assert(cy.nodes().length===2,'Cytoscape');cy.destroy();break;}
 case 'plotly':await Plotly.newPlot(target,[{x:[1,2],y:[3,4]}],{},{staticPlot:true});assert(target.querySelector('svg'),'Plotly');break;
 case 'antv-x6':{let g=new X6.Graph({container:target,width:800,height:350});g.addNode({x:20,y:20,width:80,height:40,label:'Node'});assert(g.getNodes().length===1,'X6');g.dispose();break;}
 case 'vis-network':{let n=new vis.Network(target,{nodes:[{id:1,label:'A'},{id:2,label:'B'}],edges:[{from:1,to:2}]},{physics:false});assert(n.body.data.nodes.length===2,'vis');n.destroy();break;}
 case 'codemirror':{let cm=CodeMirror(target,{value:'const x = 1;'});assert(cm.getValue().includes('const'),'CodeMirror');break;}
 case 'driver.js':{let d=window.driver.js.driver({steps:[{element:'#target',popover:{title:'介绍',description:'内容'}}]});d.drive();assert(document.querySelector('.driver-popover'),'driver');d.destroy();break;}
 case 'cropperjs':{let img=document.createElement('img');img.src='data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="red"/></svg>';target.append(img);await img.decode();let c=new Cropper.default(img);assert(c.getCropperCanvas(),'Cropper');break;}
 case 'Sortable':target.innerHTML='<li>A</li><li>B</li>';new Sortable(target);break;
 case 'Swiper':target.className='swiper';target.innerHTML='<div class="swiper-wrapper"><div class="swiper-slide">A</div><div class="swiper-slide">B</div></div>';let s=new Swiper(target);s.slideTo(1,0);assert(s.activeIndex===1,'Swiper');break;
 case 'simplebar':new SimpleBar(target);assert(target.querySelector('.simplebar-wrapper'),'Simplebar');break;
 case 'signature_pad':{let c=document.createElement('canvas');target.append(c);let pad=new SignaturePad(c);assert(pad.isEmpty(),'signature');break;}
 case 'turndown':assert(new TurndownService().turndown('<h1>Hello</h1>').includes('Hello'),'Turndown');break;
 case 'jszip':{let z=new JSZip();z.file('a.txt','中文');let b=await z.generateAsync({type:'uint8array'});let q=await JSZip.loadAsync(b);assert(await q.file('a.txt').async('string')==='中文','ZIP roundtrip');break;}
 case 'jspdf':{let doc=new jspdf.jsPDF();doc.text('Test',10,10);assert(doc.output().startsWith('%PDF-'),'PDF');break;}
 case 'html-to-image':target.innerHTML='<p>Export</p>';assert((await htmlToImage.toPng(target)).startsWith('data:image/png'),'image export');break;
 case 'flatpickr':target.innerHTML='<input>';let f=flatpickr(target.firstChild,{defaultDate:'2026-10-10'});assert(f.input.value==='2026-10-10','flatpickr');break;
 case 'sweetalert2':Swal.fire({title:'Test',showConfirmButton:false});assert(Swal.isVisible(),'SweetAlert');Swal.close();break;
 case 'highlight.js':assert(hljs.highlight('const a=1',{language:'javascript'}).value.includes('hljs'),'highlight');break;
 case 'prism':assert(Prism.highlight('const a=1',Prism.languages.javascript,'javascript').includes('token'),'Prism');break;
 case 'qrcodejs':new QRCode(target,'offline');assert(target.querySelector('canvas,table,svg'),'QR');break;
 case 'canvas-confetti':await confetti({particleCount:3,ticks:2});break;
 case 'echarts-stat':{let r=ecStat.regression('linear',[[1,3],[2,5],[3,7]]);assert(Math.abs(r.parameter.gradient-2)<1e-9,'regression slope');assert(ecStat.statistics.mean([1,2,3])===2,'mean');assert(ecStat.histogram([1,2,2,3]).bins.reduce((s,b)=>s+b.sample.length,0)===4,'histogram');let c=ecStat.clustering.hierarchicalKMeans([[0,0],[0,1],[10,10],[10,11]],2,false);assert(c.centroids.length===2,'clusters');break;}
 }
 return 'loaded; functional case completed';
},name);}

(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));base='http://127.0.0.1:'+server.address().port+'/resources';
 const executable=arg('--browser',process.env.BROWSER_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe');
 browser=await chromium.launch({headless:true,executablePath:executable});
 const index=JSON.parse(fs.readFileSync(path.join(__dirname,'../components/index.json'),'utf8'));
 for(const lib of Object.values(index.categories).flat().filter(x=>x.entrypoints.length)){
  if(['reveal.js','impress.js','wordcloud2'].includes(lib.name))continue;
  await run('library-'+lib.name,async page=>{
   await page.goto(base.replace('/resources','/__test'));
   for(const entry of [...lib.entrypoints,...lib.optional_entrypoints]){
    if(entry.kind==='css')await page.addStyleTag({url:base+'/'+entry.path});
    else if(entry.kind==='js')await page.addScriptTag({url:base+'/'+entry.path});
   }
   if(lib.global){const exists=await page.evaluate(g=>{if(g in window)return window[g]!=null;return g.split('.').reduce((v,k)=>v?.[k],window)!=null;},lib.global);if(!exists)throw Error('missing browser global '+lib.global);}
   return functional(page,lib.name);
  });
 }
 await run('fonts',async page=>{await page.goto(base.replace('/resources','/__test'));await page.addStyleTag({url:base+'/fonts/fonts.css'});return page.evaluate(async()=>{let results={};for(let font of ['Noto Sans SC','Noto Serif SC','Zhuque Fangsong','LXGW WenKai','LXGW WenKai Mono','Inter','Roboto','Merriweather','JetBrains Mono']){const faces=await document.fonts.load('24px "'+font+'"',font.includes('SC')||font.includes('WenKai')||font.includes('Fangsong')?'中文字体检查':'Report 2026');if(!faces.length||faces.some(f=>f.status!=='loaded'))throw Error('font '+font);results[font]=faces.length;}return results;});});
 await run('additional-fonts',async page=>{await page.goto(base.replace('/resources','/__test'));await page.addStyleTag({url:base+'/fonts/fonts.css'});return page.evaluate(async()=>{const results={};for(const spec of ['oblique 400 32px "Smiley Sans"','400 32px "Resource Han Rounded CN"','700 32px "Resource Han Rounded CN"']){const faces=await document.fonts.load(spec,'中文数据分析圆体标题');if(!faces.length||faces.some(f=>f.status!=='loaded'))throw Error(spec);results[spec]=faces.length;}return results;});});
 await run('data-style',async page=>{await page.goto(base+'/templates/data-style.html');await page.waitForFunction(()=>window.__RENDER_READY__);if(await page.locator('#total').textContent()!=='60'||await page.locator('#median').textContent()!=='15'||await page.locator('#rows tr').count()!==2)throw Error('analysis output');await page.screenshot({path:path.join(output,'data-style.png'),fullPage:true});return 'group totals, statistics, fonts and icons';});
 for(const viewport of [{width:1366,height:768},{width:1920,height:1080}]){
  await run('presentation-'+viewport.width,async(page,context)=>{
   await page.goto(base+'/templates/presentation-reveal.html');await page.waitForFunction(()=>window.__RENDER_READY__,{},{timeout:30000});
   await page.screenshot({path:path.join(output,'presentation-'+viewport.width+'.png')});
   await page.keyboard.press('ArrowRight');await page.waitForTimeout(250);
   if(await page.evaluate(()=>deck.getIndices().h)!==1)throw Error('navigation');
   await page.keyboard.press('ArrowRight');if(!await page.locator('.fragment.visible').count())throw Error('fragment');
   await page.evaluate(()=>deck.slide(2));await page.waitForTimeout(1000);
   const layout=await page.evaluate(()=>({width:trendChart.getWidth(),count:deck.getTotalSlides(),overflow:document.documentElement.scrollWidth>innerWidth}));
   if(layout.width<100||layout.count!==6||layout.overflow)throw Error('layout '+JSON.stringify(layout));
   await page.screenshot({path:path.join(output,'chart-slide-'+viewport.width+'.png')});
   await page.keyboard.press('Escape');if(!await page.evaluate(()=>deck.isOverview()))throw Error('overview');await page.keyboard.press('Escape');
   await page.keyboard.press('f');await page.waitForTimeout(200);const fullscreen=await page.evaluate(()=>!!document.fullscreenElement);if(!fullscreen)throw Error('fullscreen');await page.keyboard.press('f');
   const popupWait=context.waitForEvent('page',{timeout:10000});await page.keyboard.press('s');let popup=await popupWait;await popup.waitForLoadState();await popup.waitForTimeout(500);if(!await popup.title())throw Error('notes popup');await popup.close();
   await page.evaluate(()=>{document.body.classList.add('deck-dark');deck.slide(0)});await page.waitForTimeout(1000);await page.screenshot({path:path.join(output,'presentation-dark-'+viewport.width+'.png')});
   return {...layout,fullscreen,notes:true};
  },viewport);
 }
 await run('presentation-pdf',async page=>{await page.goto(base+'/templates/presentation-reveal.html?print-pdf');await page.waitForFunction(()=>window.__RENDER_READY__&&document.querySelectorAll('.pdf-page').length===6,{},{timeout:30000});const graph=await page.locator('.mermaid svg').boundingBox();if(!graph||graph.width<100||graph.height<40)throw Error('Mermaid print dimensions '+JSON.stringify(graph));await page.pdf({path:path.join(output,'presentation.pdf'),printBackground:true,preferCSSPageSize:true});return {pages:await page.locator('.pdf-page').count(),formula:await page.locator('.katex').count(),diagram:graph};});
 await run('impress',async page=>{await page.goto(base+'/templates/presentation-impress.html');await page.waitForFunction(()=>window.__RENDER_READY__);await page.keyboard.press('ArrowRight');await page.waitForTimeout(1200);if(await page.locator('.step.active').count()!==1)throw Error('active step');await page.screenshot({path:path.join(output,'impress.png')});return 'navigation';});
 await run('analysis',async page=>{await page.goto(base+'/templates/chart-analysis.html');await page.waitForFunction(()=>window.__RENDER_READY__,{},{timeout:30000});await page.screenshot({path:path.join(output,'analysis.png'),fullPage:true});return page.locator('#summary').textContent();});
 await run('base-template',async page=>{await page.goto(base+'/templates/base.html');await page.waitForSelector('svg.lucide');return 'base rendered';});
 await browser.close();server.close();const failures=checks.filter(c=>!c.passed);console.log('RESULT',checks.length-failures.length,'/',checks.length);process.exitCode=failures.length?1:0;
})().catch(async e=>{console.error(e);if(browser)await browser.close();server.close();process.exitCode=1;});
