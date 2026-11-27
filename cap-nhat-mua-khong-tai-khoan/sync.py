#!/usr/bin/env python3
"""Publish only changed source files, after all prerequisite updates succeed in staging."""
import sys, tempfile, shutil, os
from pathlib import Path
root,staged,initial=map(lambda p:Path(p).resolve(),sys.argv[1:4])
if not (root/'pom.xml').is_file():raise SystemExit('Khong tim thay du an')
files={}
for p in (staged/'src').rglob('*'):
 if p.is_symlink():raise SystemExit('Phat hien symlink; dung de bao ve du an.')
 if not p.is_file():continue
 rel=p.relative_to(staged);live=root/rel;before=initial/rel
 if not live.resolve().is_relative_to(root):raise SystemExit('Duong dan khong hop le')
 # A parallel local edit must never be overwritten.
 if live.exists()!=before.exists() or (live.is_file() and live.read_bytes()!=before.read_bytes()):raise SystemExit('File vua thay doi: '+str(rel)+'. Chua ghi file nao.')
 if not before.is_file() or before.read_bytes()!=p.read_bytes():files[rel]=p
if not files:print('Da cap nhat, khong can ghi lai.');sys.exit(0)
backup=Path(tempfile.mkdtemp(prefix='mens-store-guest-v2-backup-',dir=Path.home()))
for rel in files:
 if (root/rel).is_file():dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,dest)
print('Sao luu:',backup,flush=True)
written=[]
try:
 for rel,p in files.items():
  live=root/rel;live.parent.mkdir(parents=True,exist_ok=True);tmp=live.with_name(live.name+'.guest-v2.tmp');shutil.copy2(p,tmp);os.replace(tmp,live);written.append(rel);print('OK:',rel,flush=True)
except Exception:
 for rel in reversed(written):
  if (backup/rel).is_file():shutil.copy2(backup/rel,root/rel)
  else:(root/rel).unlink(missing_ok=True)
 raise
print('Da cap nhat',len(files),'file src. Khong thay doi .env, SQL hay volume.',flush=True)
