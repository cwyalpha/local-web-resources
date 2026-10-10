#!/usr/bin/env python3
"""Preflight and copy exact locked files; never select a version by directory order."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

DEFAULT_SERVER_DIR = Path(__file__).resolve().parents[2] / 'web-resources-server'

def contained(root, relative):
    target = (root / relative).resolve()
    if target == root or root not in target.parents:
        raise ValueError(f'Path escapes root: {relative}')
    return target

def main(library_names=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--cdnjs-root', type=Path)
    source.add_argument('--source-server', type=Path, help='Matching locked resource server.')
    parser.add_argument('--server-dir', type=Path, default=DEFAULT_SERVER_DIR)
    parser.add_argument('--lock', type=Path, default=DEFAULT_SERVER_DIR/'resources.lock.json')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    lock = json.loads(args.lock.read_text(encoding='utf-8'))
    root = (args.source_server or args.cdnjs_root).resolve()
    destination = args.server_dir.resolve()
    if not root.is_dir(): raise SystemExit(f'Source directory not found: {root}')
    libraries = {x['name']: x for x in lock['libraries']}
    planned, failures = [], []
    for rel, entry in lock['files'].items():
        parts = Path(rel).parts
        name = parts[2] if len(parts)>2 and parts[0]=='libs' else None
        if library_names is not None and name not in library_names: continue
        if args.source_server:
            candidates = [contained(root,rel)]
        else:
            if name is None: continue
            version = libraries[name].get('version')
            if not version: failures.append(f'No locked version for {name}'); continue
            relative = Path(*parts[3:])
            candidates = [contained(root,Path(name)/version/relative)]
            source_path = entry.get('package_path')
            if source_path:candidates.append(contained(root,Path(name)/version/source_path))
        selected = next((p for p in candidates if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']),None)
        if selected is None: failures.append(f'Missing or different locked file: {rel}')
        else: planned.append((selected,contained(destination,rel)))
    if failures: raise SystemExit('\n'.join(failures))
    if not planned: raise SystemExit('No matching locked files; nothing copied.')
    if not args.dry_run:
        for src,dst in planned:
            dst.parent.mkdir(parents=True,exist_ok=True)
            if src != dst: shutil.copy2(src,dst)
        destination.mkdir(parents=True,exist_ok=True)
        if args.source_server and library_names is None and args.lock.resolve()!=destination/'resources.lock.json':
            shutil.copy2(args.lock,destination/'resources.lock.json')
    print(f'{"Validated" if args.dry_run else "Copied"} {len(planned)} locked files.')

if __name__=='__main__': main()
