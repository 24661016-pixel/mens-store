#!/usr/bin/env python3
"""MENS STORE: selectable size and guest checkout. Validate every file before writing."""
import sys, json, gzip, hashlib, shutil, tempfile, os, base64
from pathlib import Path
root=Path(sys.argv[1]).resolve(); payload=Path(sys.argv[2]); expected=sys.argv[3]
if not (root/'pom.xml').is_file() or not (root/'compose.yaml').is_file(): raise SystemExit('Khong tim thay du an: '+str(root))
if hashlib.sha256(payload.read_bytes()).hexdigest()!=expected: raise SystemExit('Goi cap nhat sai checksum')
entries=json.loads(gzip.decompress(payload.read_bytes()))
pending={}
# Apply presentation edits by exact context rather than file-wide checksum if
# a previous UI update or local styling changed unrelated lines.
anchors=json.loads(gzip.decompress(base64.b64decode("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")))
def digest(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
def contextual(old, ops, specs, path):
 lines=old.splitlines(keepends=True)
 for (i,j,replacement),(oldhash,left,right) in reversed(list(zip(ops,specs))):
  n=j-i; new=replacement.splitlines(keepends=True)
  def score(at,length):
   a=0;b=0
   for off,h in enumerate(left,1):
    if at-off<0 or digest(lines[at-off])!=h:break
    a+=1
   for off,h in enumerate(right):
    if at+length+off>=len(lines) or digest(lines[at+length+off])!=h:break
    b+=1
   return a,b
  # A unique already-applied nonempty block is safe to keep. A deletion
  # is recognized only with both adjacent contexts (or the file boundary).
  applied=[]
  for at in range(len(lines)-len(new)+1):
   if lines[at:at+len(new)]!=new:continue
   a,b=score(at,len(new))
   if (a+b>=2 and (a>0 or not left) and (b>0 or not right)) or (new and a+b>=2):applied.append(at)
  candidates=[]
  for at in range(len(lines)-n+1):
   if digest(''.join(lines[at:at+n]))!=oldhash:continue
   a,b=score(at,n)
   if n==0:
    if a+b>=2 and (a>0 or not left) and (b>0 or not right):candidates.append((a+b,at))
   elif a+b>=1:candidates.append((a+b,at))
  # If the old text still occurs but the replacement is already present,
  # resolve only when a uniquely contextualized old/new position is evident.
  if len(applied)==1 and not candidates:continue
  if n==0 and len(applied)==1:continue
  if not candidates and len(new)>0 and old.count(replacement)==1:continue
  if not candidates:raise SystemExit('Khong tim thay doan ma an toan: '+path+' (vi tri '+str(i+1)+'). Chua ghi file nao.')
  best=max(x[0] for x in candidates);positions=[at for sc,at in candidates if sc==best]
  if len(positions)!=1 or (applied and n>0):raise SystemExit('Doan ma trung lap/khong ro rang: '+path+' (vi tri '+str(i+1)+'). Chua ghi file nao.')
  at=positions[0];lines[at:at+n]=new
 return ''.join(lines)
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
  elif path in anchors:
   s=contextual(old,e['ops'],anchors[path],path)
   if s!=old:pending[path]=s
   print('Giu giao dien tuy chinh:',path)
   continue
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
# A revoked or expired customer session must not force shopping to the login page.
# Only public shopping GET/HEAD requests continue as guests. Mutating requests
# must be retried with a new CSRF token; no order is automatically replayed.
filter_path='src/main/java/com/example/mens_store/config/CustomerSessionFilter.java'
filter_text=(root/filter_path).read_text(encoding='utf-8')
needle='                if (request.getRequestURI().substring(request.getContextPath().length()).startsWith("/api/")) {'
replacement='                String path = request.getRequestURI().substring(request.getContextPath().length());\n                boolean shopping = path.equals("/") || path.equals("/san-pham") || path.startsWith("/san-pham/")\n                    || path.equals("/gio-hang") || path.startsWith("/gio-hang/")\n                    || path.equals("/api/gio-hang") || path.startsWith("/api/gio-hang/")\n                    || path.equals("/dat-hang") || path.startsWith("/dat-hang/");\n                if (shopping && ("GET".equals(request.getMethod()) || "HEAD".equals(request.getMethod()))) {\n                    chain.doFilter(request, response);\n                    return;\n                }\n                if (shopping && !path.startsWith("/api/") && !path.startsWith("/san-pham/")) {\n                    response.sendRedirect(request.getContextPath() + "/gio-hang?phien-het-han");\n                    return;\n                }\n                if (path.startsWith("/api/")) {'
if replacement not in filter_text:
 if filter_text.count(needle)!=1:raise SystemExit('Khong xac nhan duoc CustomerSessionFilter. Chua ghi file nao.')
 pending[filter_path]=filter_text.replace(needle,replacement,1)
login_path='src/main/resources/templates/customer/login.html'
login=(root/login_path).read_text(encoding='utf-8')
login_link='    <p class="auth-switch"><a class="btn btn-outline block" th:href="@{/san-pham}">Tiếp tục mua hàng không cần tài khoản →</a></p>\n'
if login_link not in login:
 anchor='    <p class="auth-admin-link">'
 if login.count(anchor)!=1:raise SystemExit('Khong tim thay phan dang nhap khach. Chua ghi file nao.')
 pending[login_path]=login.replace(anchor,login_link+anchor,1)
fragment_path='src/main/resources/templates/fragments.html'
fragment=pending.get(fragment_path,(root/fragment_path).read_text(encoding='utf-8'))
notice='    <div class="alert bad" role="status" th:if="${param[\'phien-het-han\'] != null}">Phiên tài khoản trước đã kết thúc. Bạn có thể tiếp tục mua hàng không cần đăng nhập. Hãy chọn lại sản phẩm.</div>\n'
if notice not in fragment:
 anchor='<div th:fragment="alerts" class="container alerts">\n'
 if fragment.count(anchor)!=1:raise SystemExit('Khong tim thay khung thong bao. Chua ghi file nao.')
 pending[fragment_path]=fragment.replace(anchor,anchor+notice,1)
# Confirm the public routes and size field exist before any writes. Do not
# broaden authorization to admin/account or disable CSRF.
security_path='src/main/java/com/example/mens_store/config/SecurityConfig.java'
security=pending.get(security_path,(root/security_path).read_text(encoding='utf-8'))
assert '.requestMatchers("/gio-hang", "/gio-hang/**", "/api/gio-hang", "/api/gio-hang/**", "/dat-hang", "/dat-hang/**").permitAll()' in security, 'Guest routes missing'
assert '.requestMatchers("/quan-tri", "/quan-tri/**").hasRole("ADMIN")' in security, 'Admin guard missing'
assert '.requestMatchers("/tai-khoan", "/tai-khoan/**", "/tro-ly", "/tro-ly/**").hasRole("CUSTOMER")' in security, 'Account guard missing'

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
