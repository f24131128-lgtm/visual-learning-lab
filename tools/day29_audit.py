"""Redacted local repository, dependency metadata and frozen-record audit."""
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/day29';OUT.mkdir(parents=True,exist_ok=True)


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def main():
    pattern=re.compile(rb'(?<![A-Za-z0-9])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}')
    tracked=git('ls-files','-z').split(b'\0')
    hits=[]; scanned=0
    for encoded in tracked:
        if not encoded:continue
        name=encoded.decode('utf-8');path=ROOT/name
        if path.is_file() and path.stat().st_size<=5*1024*1024:
            scanned+=1
            if pattern.search(path.read_bytes()):hits.append(dict(path=name,scope='current',classification='requires review; value omitted'))
    # Scan unique historical blobs, never echo blob content or matched values.
    historical=0; historical_hits=[]
    objects=git('rev-list','--objects','--all').decode('utf-8').splitlines()
    batch=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    for line in objects:
        parts=line.split(' ',1)
        if len(parts)!=2:continue
        oid,name=parts
        batch.stdin.write((oid+'\n').encode());batch.stdin.flush()
        header=batch.stdout.readline().split()
        size=int(header[2]);body=batch.stdout.read(size);batch.stdout.read(1)
        if header[1]!=b'blob' or size>5*1024*1024:continue
        historical+=1
        if pattern.search(body):
            commit=git('log','-1','--format=%H','--find-object='+oid,'--all').decode().strip()
            historical_hits.append(dict(path=name,blob=oid,commit=commit,classification='indicator only; value omitted'))
    batch.stdin.close();batch.wait()
    config=ROOT/'.streamlit/secrets.toml'
    summary=dict(tracked_files=scanned,historical_blobs=historical,indicators=hits+historical_hits,
        tracked_secret_paths=[v.decode() for v in tracked if v and ('secrets.toml' in v.decode() or v.decode().endswith('.env'))],
        local_secret_file_present=config.exists(),environment_key_present=bool(os.environ.get('OPENAI_API_KEY')),
        rotation_performed=False,scope='All reachable refs, <=5 MiB blobs; no deleted/unreachable-object forensics')
    (OUT/'secrets-results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    vendored=json.loads((ROOT/'manipulation/frontend/vendor-manifest.json').read_text())
    vendor=[]
    for entry in vendored['files']:
        file=ROOT/'manipulation/frontend'/entry['path']
        vendor.append(dict(path=entry['path'],pass_hash=hashlib.sha256(file.read_bytes()).hexdigest()==entry['sha256']))
    installed=[]
    for package in ('pypdfium2','pypdf','streamlit','openai','pillow','numpy','plotly','streamlit-flow-component'):
        dist=metadata.distribution(package)
        installed.append(dict(name=package,version=dist.version,license=dist.metadata.get('License-Expression') or dist.metadata.get('License'),
            license_files=[str(p) for p in dist.files or [] if 'LICENSE' in str(p).upper() or 'COPYING' in str(p).upper()]))
    (OUT/'dependency-metadata.json').write_text(json.dumps(dict(installed=installed,jsxgraph=vendor),indent=2)+'\n',encoding='utf-8')
    report=json.loads((ROOT/'.day29-local/install-report.json').read_text(encoding='utf-8'))
    pins=sorted(e['metadata']['name']+'=='+e['metadata']['version'] for e in report['install'])
    (ROOT/'requirements-day29-lock.txt').write_text('# Resolved clean Windows Python 3.12 environment; re-audit other platform wheels.\n'+'\n'.join(pins)+'\n',encoding='utf-8')
    # Freeze files are read, never rewritten.
    frozen=json.loads((ROOT/'docs/day28/freeze-manifest.json').read_text())['files_sha256']
    checks={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in frozen.items()}
    (OUT/'historical-integrity.json').write_text(json.dumps(dict(day28_files=checks,day28_500_pass_log_sha256=hashlib.sha256((ROOT/'docs/day28-ai-red-team/full-regression.log').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(dict(scanned_current=scanned,scanned_historical=historical,secret_indicators=len(hits+historical_hits),vendor_pass=all(v['pass_hash'] for v in vendor),frozen_pass=all(checks.values()))))


if __name__=='__main__':main()
