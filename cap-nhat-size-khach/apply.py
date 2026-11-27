#!/usr/bin/env python3
"""MENS STORE: selectable size and guest checkout. Validate every file before writing."""
import sys, json, gzip, hashlib, shutil, tempfile, os
from pathlib import Path
root=Path(sys.argv[1]).resolve(); payload=Path(sys.argv[2]); expected=sys.argv[3]
if not (root/'pom.xml').is_file() or not (root/'compose.yaml').is_file(): raise SystemExit('Khong tim thay du an: '+str(root))
if hashlib.sha256(payload.read_bytes()).hexdigest()!=expected: raise SystemExit('Goi cap nhat sai checksum')
entries=json.loads(gzip.decompress(payload.read_bytes()))
pending={}
# Accept the verified layout from the earlier cap-nhat-mua-hang update.
# Exact hashes prevent applying line offsets to an unknown template.
variants={
 'src/main/resources/templates/cart.html': ('56178892d9f953e7cb506c6e20973a8642bfaea11efa22d4cf008ccc68b86af9','232959a4184de00aaa05e1e5f7861f0f2518d49247d3c0dedfb90a98f70487c4',0),
 'src/main/resources/templates/checkout.html': ('d20a5e408c4feb3c49465102eec65c3aff66898f48e71ac68c49aab6eb2fb0c4','d45d048a644eca2e8adeba53fdea8445e352d8a3b0c2859494b6c612df6e4e43',1),
 'src/main/resources/templates/detail.html': ('a8f99d8bab09a1bfa00cd35107636642b9dac47e904296e41c743f08f991c9c1','63f770db3e5ae96c0950d98d0402810f36a74559eb29db23b6572289d6f81ed0',0),
}
for path,e in entries.items():
 p=root/path
 if not path.startswith('src/') or not p.resolve().is_relative_to(root): raise SystemExit('Duong dan khong hop le')
 old=p.read_text(encoding='utf-8') if p.exists() else None
 if 'hunks' in e:
  if old is None:raise SystemExit('Thieu file: '+path+'. Can cap nhat Mua ngay, Ton kho va Bang size truoc.')
  s=old
  for before,after in e['hunks']:
   # The previous purchase/admin updates may place another CSS link between these two links.
   if path=='src/main/resources/templates/fragments.html' and '/assets/css/size-picker.css' in after:
    before='    <link rel="stylesheet" th:href="@{/assets/css/size-guide.css}">\n'
    after=before+'    <link rel="stylesheet" th:href="@{/assets/css/size-picker.css}">\n'
   if after in s:continue
   if s.count(before)!=1:raise SystemExit('Khong khop phien ban: '+path+'. Chua ghi file nao. Gui ket qua cho ChatGPT.')
   s=s.replace(before,after,1)
 elif 'ops' in e:
  if old is None:raise SystemExit('Thieu file: '+path+'. Can cap nhat Mua ngay, Ton kho va Bang size truoc.')
  oldsha=hashlib.sha256(old.encode()).hexdigest()
  variant=variants.get(path)
  if oldsha==e['newsha'] or (variant and oldsha==variant[1]):continue
  if oldsha==e['oldsha']:
   shift=0; target=e['newsha']
  elif variant and oldsha==variant[0]:
   shift=variant[2]; target=variant[1]; print('Tuong thich bo cuc mua hang cu:',path)
  else:
   raise SystemExit('Khong khop phien ban: '+path+' (SHA-256 '+oldsha+'). Chua ghi file nao. Gui ket qua cho ChatGPT.')
  lines=old.splitlines(keepends=True)
  for i,j,text in reversed(e['ops']):lines[i+shift:j+shift]=[text]
  s=''.join(lines)
  if hashlib.sha256(s.encode()).hexdigest()!=target:raise SystemExit('Loi du lieu cap nhat: '+path)
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
