#!/usr/bin/env python3
"""Regression tests for lock copy safety, case-sensitive references and regeneration."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parent
SKILL=SCRIPTS.parent
SERVER=SKILL.parent/'web-resources-server'

def workspace_temp():
    # An explicit directory also supports Windows sandbox environments whose
    # system TEMP allows creation but denies subsequent child access.
    parent=Path(os.environ.get('RESOURCE_TEST_TMP',str(Path.cwd()/'.resource-test-tmp'))).resolve()
    parent.mkdir(parents=True,exist_ok=True)
    return tempfile.TemporaryDirectory(prefix='web-resource-test-',dir=parent)

def run(script,*args):
    return subprocess.run([sys.executable,'-X','utf8',str(SCRIPTS/script),*map(str,args)],capture_output=True,text=True,encoding='utf-8')

class MaintenanceTests(unittest.TestCase):
    def test_copy_preflight_then_complete(self):
        with workspace_temp() as tmp:
            root=Path(tmp);mirror=root/'mirror';destination=root/'out';destination.mkdir()
            (destination/'sentinel').write_text('unchanged')
            assets={'libs/test/demo/core.js':b'window.Demo = 1;', 'libs/test/demo/fonts/demo.woff2':b'fixture-font'}
            lock={'libraries':[{'name':'demo','version':'1.2.3'}],'files':{p:{'sha256':hashlib.sha256(data).hexdigest()} for p,data in assets.items()}}
            lockpath=root/'lock.json';lockpath.write_text(json.dumps(lock))
            for rel,data in assets.items():
                p=mirror/'demo/1.2.3'/Path(*Path(rel).parts[3:]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            font=mirror/'demo/1.2.3/fonts/demo.woff2';font.write_bytes(b'wrong')
            result=run('copy_resources.py','--cdnjs-root',mirror,'--server-dir',destination,'--lock',lockpath)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual([p.name for p in destination.iterdir()],['sentinel'])
            font.write_bytes(assets['libs/test/demo/fonts/demo.woff2'])
            result=run('copy_resources.py','--cdnjs-root',mirror,'--server-dir',destination,'--lock',lockpath)
            self.assertEqual(result.returncode,0,result.stderr)
            for rel,data in assets.items():self.assertEqual((destination/rel).read_bytes(),data)

    def test_validation_detects_wrong_case_and_checksum(self):
        with workspace_temp() as tmp:
            root=Path(tmp);skill=root/'skill';server=root/'server';(skill/'components').mkdir(parents=True);server.mkdir();(server/'templates').mkdir()
            p=server/'libs/demo/asset.js';p.parent.mkdir(parents=True);p.write_text('window.a=1;')
            (skill/'SKILL.md').write_text('`{BASE_URL}/libs/demo/Asset.js`')
            (skill/'components/index.json').write_text('{"categories":{}}')
            (server/'resources.lock.json').write_text(json.dumps({'libraries':[],'files':{'libs/demo/asset.js':{'sha256':'incorrect'}}}))
            result=run('validate_bundle.py','--skill-dir',skill,'--server-dir',server)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('wrong-case path',result.stdout)
            self.assertIn('Checksum mismatch',result.stdout)

    def test_regeneration_preserves_metadata_and_references(self):
        with workspace_temp() as tmp:
            copy=Path(tmp)/'skill';shutil.copytree(SKILL,copy,ignore=shutil.ignore_patterns('__pycache__'))
            expected={p.relative_to(SKILL).as_posix():p.read_bytes() for p in (SKILL/'components').glob('*') if p.is_file()}
            result=run('build_component_index.py','--skill-dir',copy,'--server-dir',SERVER)
            self.assertEqual(result.returncode,0,result.stderr)
            for rel,data in expected.items():self.assertEqual((copy/rel).read_bytes(),data,rel)
            for p in (SKILL/'references').glob('*.md'):self.assertEqual((copy/'references'/p.name).read_bytes(),p.read_bytes())

if __name__=='__main__':unittest.main(verbosity=2)
