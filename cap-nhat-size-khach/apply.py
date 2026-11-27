#!/usr/bin/env python3
"""MENS STORE: selectable size and guest checkout. Validate every file before writing."""
import sys, json, gzip, hashlib, shutil, tempfile, os
from pathlib import Path
root=Path(sys.argv[1]).resolve(); payload=Path(sys.argv[2]); expected=sys.argv[3]
if not (root/'pom.xml').is_file() or not (root/'compose.yaml').is_file(): raise SystemExit('Khong tim thay du an: '+str(root))
if hashlib.sha256(payload.read_bytes()).hexdigest()!=expected: raise SystemExit('Goi cap nhat sai checksum')
entries=json.loads(gzip.decompress(payload.read_bytes()))
pending={}
for path,e in entries.items():
 p=root/path
 if not path.startswith('src/') or not p.resolve().is_relative_to(root): raise SystemExit('Duong dan khong hop le')
 old=p.read_text(encoding='utf-8') if p.exists() else None
 if 'hunks' in e:
  if old is None:raise SystemExit('Thieu file: '+path+'. Can cap nhat Mua ngay, Ton kho va Bang size truoc.')
  s=old
  for before,after in e['hunks']:
   if after in s:continue
   if s.count(before)!=1:raise SystemExit('Khong khop phien ban: '+path+'. Chua ghi file nao. Gui ket qua cho ChatGPT.')
   s=s.replace(before,after,1)
 elif 'ops' in e:
  if old is None:raise SystemExit('Thieu file: '+path+'. Can cap nhat Mua ngay, Ton kho va Bang size truoc.')
  oldsha=hashlib.sha256(old.encode()).hexdigest()
  if oldsha==e['newsha']:continue
  if oldsha!=e['oldsha']:raise SystemExit('Khong khop phien ban: '+path+'. Chua ghi file nao. Gui ket qua cho ChatGPT.')
  lines=old.splitlines(keepends=True)
  for i,j,text in reversed(e['ops']):lines[i:j]=[text]
  s=''.join(lines)
  if hashlib.sha256(s.encode()).hexdigest()!=e['newsha']:raise SystemExit('Loi du lieu cap nhat: '+path)
 else:
  s=e['new']
  if old==s:continue
  if 'oldsha' in e:
   if old is None or hashlib.sha256(old.encode()).hexdigest()!=e['oldsha']:raise SystemExit('Khong khop phien ban: '+path+'. Chua ghi file nao. Gui ket qua cho ChatGPT.')
  elif old is not None:raise SystemExit('File da ton tai: '+path+'. Chua ghi file nao.')
 if s!=old:pending[path]=s
if not pending:print('Da cap nhat');sys.exit(0)
backup=Path(tempfile.mkdtemp(prefix='mens-store-size-guest-backup-',dir=Path.home()));print('Sao luu:',backup)
for path in pending:
 p=root/path
 if p.is_file():dest=backup/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
written=[]
try:
 for path,s in pending.items():
  p=root/path;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.size-guest.tmp');tmp.write_text(s,encoding='utf-8');
  if p.exists():shutil.copymode(p,tmp)
  os.replace(tmp,p);written.append(path);print('OK:',path)
except Exception:
 for path in reversed(written):
  if (backup/path).is_file():shutil.copy2(backup/path,root/path)
  else:(root/path).unlink(missing_ok=True)
 raise
print('Hoan tat. MySQL se tu them bang gio theo size va cot kich_co khi khoi dong. Khong xoa du lieu cu.')
