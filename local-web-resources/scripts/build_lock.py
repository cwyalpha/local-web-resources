#!/usr/bin/env python3
"""Build a release lock from reviewed provenance; validation remains a separate step."""
import argparse
import hashlib
import json
from pathlib import Path

def main():
    base=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-dir',type=Path,default=base/'web-resources-server')
    parser.add_argument('--skill-dir',type=Path,default=base/'local-web-resources')
    parser.add_argument('--sources',type=Path,required=True,help='Reviewed per-file provenance JSON maintained locally; not bundled with the public repository.')
    args=parser.parse_args();server=args.server_dir.resolve()
    sources=json.loads(args.sources.read_text(encoding='utf-8'))
    index=json.loads((args.skill_dir/'components/index.json').read_text(encoding='utf-8'))
    libraries=[{'name':x['name'],'version':x['version']} for group in index['categories'].values() for x in group]
    files={}
    for p in sorted(server.rglob('*')):
        if not p.is_file() or p.name=='resources.lock.json':continue
        relative=p.relative_to(server).as_posix()
        if relative not in sources:raise SystemExit('Missing reviewed provenance: '+relative)
        data=p.read_bytes()
        files[relative]={**sources[relative],'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    lock={'schema_version':1,'release':'local-web-resources-v5','libraries':libraries,'files':files}
    (server/'resources.lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Locked {len(files)} files, {len(libraries)} libraries. Run validate_bundle.py separately.')

if __name__=='__main__':main()
