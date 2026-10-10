#!/usr/bin/env python3
"""Check paired metadata, exact-case paths, templates, CSS, and the file lock."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
from validate_resources import documented_paths, css_subresources

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--server-dir',type=Path,default=Path(__file__).resolve().parents[2]/'web-resources-server')
    parser.add_argument('--skip-lock',action='store_true')
    parser.add_argument('--json-output',type=Path)
    args=parser.parse_args();skill=args.skill_dir.resolve();server=args.server_dir.resolve()
    failures=[]; files={p.relative_to(server).as_posix():p for p in server.rglob('*') if p.is_file()}
    refs=set(documented_paths(skill))
    index=json.loads((skill/'components/index.json').read_text(encoding='utf-8'))
    libraries=[x for v in index['categories'].values() for x in v]
    for lib in libraries:
        refs.update(lib['files']);refs.update(e['path'] for e in lib['entrypoints']+lib['optional_entrypoints'])
        if not (skill/'components'/lib['file']).is_file():failures.append('Missing component '+lib['file'])
        sizes=sum(files[p].stat().st_size for p in lib['files'] if p in files)
        if lib['file_count']!=len(lib['files']):failures.append('File count mismatch '+lib['name'])
        if abs(sizes/1024-lib['size_kb'])>0.06*len(lib['files'])+0.1:failures.append('Size mismatch '+lib['name'])
    for template in (server/'templates').glob('*'):
        if template.suffix not in ['.html','.css','.js']:continue
        text=template.read_text(encoding='utf-8')
        refs.update(re.findall(r'\{BASE_URL\}/([A-Za-z0-9_./@+\-]+)',text))
        if '.agent/skills/' in text:failures.append('Old skill URL in '+template.name)
        if template.suffix=='.html':
            for url in re.findall(r'(?:src|href)\s*=\s*["\x27]([^"\x27]+)',text):
                if url.startswith(('http:','https:','//')):failures.append('External template dependency '+url)
    refs.discard('libs/js-core/katex')  # Reveal local setting names a directory.
    for ref in sorted(refs):
        if ref not in files:failures.append('Missing or wrong-case path '+ref)
    for css,url,target in css_subresources(server):failures.append(f'CSS missing: {css.relative_to(server)} -> {url}')
    for css in server.rglob('*.css'):
        if not css.is_file():continue
        text=re.sub(r'/\*.*?\*/','',css.read_text(encoding='utf-8',errors='replace'),flags=re.S)
        for raw in re.findall(r'url\(\s*["\x27]?([^\)"\x27]+)',text):
            if raw.startswith(('http:','https:','//')):failures.append(f'External CSS dependency: {css.relative_to(server)} -> {raw}')
            elif not raw.startswith(('data:','#')):
                target=(css.parent/unquote(urlsplit(raw).path)).resolve()
                if server in target.parents and target.relative_to(server).as_posix() not in files:failures.append('Wrong-case CSS target '+str(target))
    for md in skill.rglob('*.md'):
        text=md.read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r'^[a-z]+:',link) or link.startswith('#'):continue
            rel=unquote(link.split('#')[0])
            if rel and not (md.parent/rel).is_file():failures.append(f'Broken document link {md.relative_to(skill)} -> {rel}')
    lockpath=server/'resources.lock.json'
    if not args.skip_lock:
        if not lockpath.is_file():failures.append('Missing resources.lock.json')
        else:
            lock=json.loads(lockpath.read_text(encoding='utf-8'))
            for rel,info in lock['files'].items():
                if rel not in files:failures.append('Locked file missing '+rel)
                elif hashlib.sha256(files[rel].read_bytes()).hexdigest()!=info['sha256']:failures.append('Checksum mismatch '+rel)
            failures.extend('Untracked server file '+p for p in sorted(set(files)-set(lock['files'])-{'resources.lock.json'}))
            versions={x['name']:x['version'] for x in lock['libraries']}
            for lib in libraries:
                if lib['version']!=versions.get(lib['name']):failures.append('Version mismatch '+lib['name'])
    report={'libraries':len(libraries),'files':len(files),'resource_references':len(refs),'failures':failures,'passed':not failures}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True,exist_ok=True)
        args.json_output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(bool(failures))

if __name__=='__main__':main()
