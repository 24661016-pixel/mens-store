#!/usr/bin/env python3
"""Smoke-check guest purchase in the running MENS STORE. Never submit a real order."""
import sys,time,re,json,http.cookiejar,urllib.request,urllib.parse,urllib.error
from html.parser import HTMLParser
BASE='http://127.0.0.1:8080'
jar=http.cookiejar.CookieJar()
client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def fetch(path,params=None):
 data=None if params is None else urllib.parse.urlencode(params).encode()
 req=urllib.request.Request(BASE+path,data=data,headers={'User-Agent':'MENS-STORE-Guest-Smoke-Check'})
 with client.open(req,timeout=8) as r:
  return urllib.parse.urlsplit(r.geturl()).path,r.read().decode('utf-8')

class PurchaseForm(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.active=False;self.found=False;self.hidden={};self.sizes=[];self.buy=False;self.available=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='form' and 'direct-buy-form' in (a.get('class') or '').split():self.active=True;self.found=True
  if not self.active:return
  if tag=='input':
   if a.get('type')=='hidden' and a.get('name'):self.hidden[a['name']]=a.get('value','')
   if a.get('name')=='size' and a.get('type')=='radio' and 'disabled' not in a and a.get('value'):self.sizes.append(a['value'])
   if a.get('name')=='quantity' and 'disabled' not in a and int(a.get('max') or '1')>0:self.available=True
  if tag=='button' and a.get('formaction')=='/dat-hang/mua-ngay/bat-dau' and 'disabled' not in a:self.buy=True
 def handle_endtag(self,tag):
  if tag=='form':self.active=False

def main():
 deadline=time.monotonic()+100
 while True:
  try:
   path,html=fetch('/san-pham')
   if path!='/san-pham':raise RuntimeError('Trang san pham bi chuyen den '+path)
   break
  except (OSError,urllib.error.URLError,RuntimeError):
   if time.monotonic()>deadline:raise RuntimeError('Web chua san sang o cong 8080. Xem docker compose logs --tail=100 web')
   time.sleep(3)
 path,data=fetch('/api/gio-hang');cart=json.loads(data)
 assert path=='/api/gio-hang' and cart.get('count')==0,'Khong mo duoc gio khach moi'
 path,_=fetch('/gio-hang');assert path=='/gio-hang','Gio hang yeu cau dang nhap'
 print('PASS: mo gio hang khong can tai khoan',flush=True)
 ids=list(dict.fromkeys(re.findall(r'href="/san-pham/(\d+)(?:\?[^" ]*)?"',html)))
 if not ids:raise RuntimeError('Khong tim thay san pham cong khai de kiem tra.')
 choices=[]
 for product_id in ids[:100]:
  path,detail=fetch('/san-pham/'+product_id)
  if path!='/san-pham/'+product_id:continue
  f=PurchaseForm();f.feed(detail)
  if f.found and f.available and f.buy and (f.sizes or f.hidden.get('size')):choices.append((product_id,f))
  if choices and f.sizes and f.available and f.buy:break
 if not choices:raise RuntimeError('Khong tim thay san pham con hang co nut Mua ngay. Kiem tra ton kho/giao dien.')
 product_id,form=next((x for x in choices if x[1].sizes),choices[0])
 # Fetch it again for a current CSRF token. No customer credentials are used.
 _,detail=fetch('/san-pham/'+product_id);form=PurchaseForm();form.feed(detail)
 size='M' if 'M' in form.sizes else (form.sizes[0] if form.sizes else form.hidden['size'])
 params={**form.hidden,'id':product_id,'quantity':'1','size':size}
 assert any('csrf' in k.lower() and v for k,v in params.items()),'Thieu CSRF token'
 path,checkout=fetch('/dat-hang/mua-ngay/bat-dau',params)
 assert path=='/dat-hang/mua-ngay','Mua ngay bi chuyen den '+path
 assert all(re.search(r'name="'+field+r'"',checkout) for field in ['fullName','phone','address','checkoutToken']),'Thieu form giao hang'
 assert 'Xác nhận đặt hàng' in checkout,'Thieu nut xac nhan'
 path,data=fetch('/api/gio-hang');assert json.loads(data)['count']==0,'Mua ngay lam thay doi gio'
 print('PASS: Mua ngay -> nhap thong tin giao hang khi chua dang nhap; gio van trong',flush=True)
 if form.sizes: print('PASS: chon size bang nut, size '+size+' da duoc truyen den thanh toan',flush=True)
 else: print('CHUA KIEM TRA SIZE AO/QUAN: chi tim thay phu kien con hang',flush=True)
 _,detail=fetch('/san-pham/'+product_id);form=PurchaseForm();form.feed(detail)
 params={**form.hidden,'id':product_id,'quantity':'1','size':size,'stayOnDetail':'true'}
 path,_=fetch('/gio-hang/them',params);assert path in ('/san-pham/'+product_id,'/gio-hang'),'Them gio bi chuyen den '+path
 _,data=fetch('/api/gio-hang');items=json.loads(data)['items'];assert any(str(x['id'])==product_id and x['size']==size and x['qty']==1 for x in items),'Size khong duoc luu vao gio khach'
 print('PASS: them gio va luu size khong can dang nhap',flush=True)
 # Guest must not be allowed to open admin; redirects may end at admin login.
 path,_=fetch('/quan-tri');assert path=='/dang-nhap','Kiem tra bao ve admin that bai: '+path
 print('PASS: quan tri van yeu cau dang nhap',flush=True)
 print('KIEM TRA THANH CONG. Khong tao don hang that; khong thanh toan.',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('KIEM TRA CHUA DAT:',str(e),file=sys.stderr);sys.exit(1)
