#!/usr/bin/env python3
"""Rebuild the known MENS STORE 2.1.1 shopping module without local patch conflicts."""
from pathlib import Path
import gzip, hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, zipfile

J = 'src/main/java/com/example/mens_store/'
T = 'src/main/resources/templates/'
A = 'src/main/resources/static/assets/'
OLD_ROLE = '''.requestMatchers("/tai-khoan", "/tai-khoan/**", "/gio-hang", "/gio-hang/**",
                        "/api/gio-hang", "/api/gio-hang/**", "/dat-hang", "/dat-hang/**",
                        "/tro-ly", "/tro-ly/**").hasRole("CUSTOMER")'''
PUBLIC = '.requestMatchers("/gio-hang", "/gio-hang/**", "/api/gio-hang", "/api/gio-hang/**", "/dat-hang", "/dat-hang/**").permitAll()'
ACCOUNT = '.requestMatchers("/tai-khoan", "/tai-khoan/**", "/tro-ly", "/tro-ly/**").hasRole("CUSTOMER")'
ADMIN = '.requestMatchers("/quan-tri", "/quan-tri/**").hasRole("ADMIN")'
COMMENT = '.requestMatchers(org.springframework.http.HttpMethod.POST, "/san-pham/*/binh-luan").hasRole("CUSTOMER")'
FILTER_OLD = '                if (request.getRequestURI().substring(request.getContextPath().length()).startsWith("/api/")) {'
FILTER_NEW = '''                String path = request.getRequestURI().substring(request.getContextPath().length());
                boolean shopping = path.equals("/") || path.equals("/san-pham") || path.startsWith("/san-pham/")
                    || path.equals("/gio-hang") || path.startsWith("/gio-hang/")
                    || path.equals("/api/gio-hang") || path.startsWith("/api/gio-hang/")
                    || path.equals("/dat-hang") || path.startsWith("/dat-hang/");
                if (shopping && ("GET".equals(request.getMethod()) || "HEAD".equals(request.getMethod()))) {
                    chain.doFilter(request, response);
                    return;
                }
                if (shopping && !path.startsWith("/api/") && !path.startsWith("/san-pham/")) {
                    response.sendRedirect(request.getContextPath() + "/gio-hang?phien-het-han");
                    return;
                }
                if (path.startsWith("/api/")) {'''

def cmd(*args, cwd=None, env=None):
    subprocess.run(args, cwd=cwd, env=env, check=True)

def capture(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd)

def read(root, path):
    return (root/path).read_text(encoding='utf-8')

def put(root, path, value):
    p=root/path;p.parent.mkdir(parents=True, exist_ok=True);p.write_text(value, encoding='utf-8')

def once(s, old, new, label):
    if new in s:return s
    if s.count(old)!=1:raise RuntimeError('Khong nhan dien duoc '+label)
    return s.replace(old,new,1)

def project_ok(p):
    return (p/'pom.xml').is_file() and (p/'compose.yaml').is_file() and (p/J/'config/SecurityConfig.java').is_file()

def find_project(root):
    args=['docker','ps','--filter','label=com.docker.compose.project=mens-store','--filter','label=com.docker.compose.service=web','--format','{{.ID}}']
    ids=capture(*args).decode().split()
    if not ids:
        ids=capture(*(args[:2]+['-a']+args[2:])).decode().split()
    candidates=set()
    for id in ids:
        value=capture('docker','inspect','--format','{{index .Config.Labels "com.docker.compose.project.working_dir"}}',id).decode().strip()
        if value and value!='<no value>':
            p=Path(value).resolve()
            if p.is_relative_to(root) and project_ok(p):candidates.add(p)
            else:raise RuntimeError('Container web o thu muc khac: '+value+'. Dung de tranh sua nham.')
    if not candidates:
        candidates={p for p in (root,root/'mens-store') if project_ok(p)}
    if len(candidates)!=1:raise RuntimeError('Khong xac dinh duy nhat thu muc web: '+str(candidates))
    return candidates.pop()

def prepare_reference(root):
    # The original GitHub ZIP used phone login. Reproduce the exact Gmail checkout
    # reference for the versioned patches; never change the live account service.
    for path in ('controller/CheckoutController.java','controller/CustomerOrderController.java','service/CartService.java','service/OrderService.java'):
        p=J+path
        put(root,p,once(read(root,p),'customers.findByPhone(auth.getName())','customers.findAuthenticatedAccount(auth)',p))
    p=J+'config/SecurityConfig.java';s=read(root,p)
    s=once(s,'return customers.findByPhone(username).map(CustomerPrincipal::new)','return customers.findByEmail(username)\n                .filter(account -> !CustomerAccountService.normalizeEmail(account.email()).endsWith("@mensstore.local"))\n                .map(CustomerPrincipal::new)',p)
    s=once(s,'.usernameParameter("soDienThoai")','.usernameParameter("username")',p);put(root,p,s)

def repair_security(s):
    if ADMIN not in s or COMMENT not in s:raise RuntimeError('Khong xac nhan duoc quyen ADMIN/binh luan trong SecurityConfig')
    if OLD_ROLE in s:
        if PUBLIC in s:s=s.replace(PUBLIC+'\n                    ','',1)
        s=s.replace(OLD_ROLE,PUBLIC+'\n                    '+ACCOUNT,1)
    elif PUBLIC not in s and ACCOUNT in s:
        s=s.replace(ACCOUNT,PUBLIC+'\n                    '+ACCOUNT,1)
    if s.count(PUBLIC)!=1 or ACCOUNT not in s or not(s.index(ADMIN)<s.index(PUBLIC)<s.index(ACCOUNT)):
        raise RuntimeError('Khong xac nhan duoc thu tu phan quyen gio hang/thanh toan')
    for rule in re.findall(r'\.requestMatchers\((.*?)\)\s*\.hasRole\("CUSTOMER"\)',s,re.S):
        # The regex may span a permitAll chain; inspect only the final matcher.
        rule=rule.rsplit('.requestMatchers(',1)[-1]
        if any(x in rule for x in ('"/gio-hang','"/api/gio-hang','"/dat-hang')):
            raise RuntimeError('Van con quy tac bat dang nhap de mua hang')
    return s.replace('Vui lòng đăng nhập để sử dụng giỏ hàng.','Phiên mua sắm đã thay đổi. Vui lòng tải lại trang.')

def repair_filter(s):
    if FILTER_NEW in s or ('boolean shopping =' in s and '"/dat-hang/"' in s and 'chain.doFilter(request, response);' in s):return s
    return once(s,FILTER_OLD,FILTER_NEW,'CustomerSessionFilter')

MODULE_JAVA = [
 'config/SizeSchema.java','controller/CartApiController.java','controller/CartController.java',
 'controller/CheckoutController.java','controller/CheckoutSupport.java','controller/CustomerOrderController.java',
 'controller/DirectCheckoutController.java','controller/ShopController.java','model/CartItem.java',
 'model/CartKey.java','model/OrderLine.java','model/SizeGuide.java','repository/CartRepository.java',
 'repository/OrderRepository.java','service/CartService.java','service/OrderService.java']
MODULE_RES = [T+x for x in ('cart.html','checkout.html','detail.html','size-guide.html','success.html')]+[A+x for x in ('css/direct-buy.css','css/stock-display.css','css/size-guide.css','css/size-picker.css','js/stock-quantity.js','js/home-store.js')]

# Keep the home design, account controls, dynamic categories and admin navigation.
def repair_home(s, patch):
    for old,new in patch[T+'home.mens.html']['hunks']:
        if old in s:s=s.replace(old,new,1)
    s=s.replace("? 'Thêm giỏ' : 'Tạm hết hàng'", "? 'Chọn size' : 'Tạm hết hàng'")
    s=s.replace('>Thêm giỏ</span>','>Chọn size</span>').replace('Tiếp tục đặt hàng','Xem giỏ hàng')
    s=s.replace('Giỏ hàng được lưu riêng theo tài khoản. Đăng nhập lại để tiếp tục mua sắm.','Khách có thể mua không cần tài khoản. Giỏ của khách được lưu trong phiên trình duyệt.')
    s=s.replace('Ghi size, màu mong muốn trong ghi chú đơn hàng để cửa hàng xác nhận.','Chọn size trực tiếp. Mua ngay không cần đăng nhập.')
    s=re.sub(r'@\{/assets/js/home-store\.js(?:\([^}]*\))?\}',"@{/assets/js/home-store.js(v='guest-v3')}",s)
    s=re.sub(r'(?<!th:)src="/assets/js/home-store\.js(?:\?[^" ]*)?"','src="/assets/js/home-store.js?v=guest-v3"',s)
    if 'home-store.js' not in s:raise RuntimeError('Khong tim thay JavaScript trang chu')
    link='    <link rel="stylesheet" th:href="@{/assets/css/stock-display.css}">\n'
    if '/assets/css/stock-display.css' not in s:s=once(s,'</head>',link+'</head>','head trang chu')
    return s

def repair_fragments(s,patch):
    for file in ('size-guide.css','size-picker.css','direct-buy.css','stock-display.css'):
        if '/assets/css/'+file not in s:
            s=once(s,'</head>','    <link rel="stylesheet" th:href="@{/assets/css/'+file+'}">\n</head>','head fragments')
    old,new=patch[T+'fragments.html']['hunks'][1]
    if old in s:s=s.replace(old,new,1)
    elif new not in s and 'Chọn size / Mua hàng' not in s:
        # Preserve the surrounding card; only replace the old add form.
        pattern=r'<form\b[^>]*th:action="@\{/gio-hang/them\}"[^>]*>\s*.*?</form>'
        replacement=new[new.index('<a class='):new.index('\n    </div>')]
        s,n=re.subn(pattern,lambda _:replacement,s,count=1,flags=re.S)
        if n!=1:raise RuntimeError('Khong tim thay nut chon san pham trong fragments')
    if 'Chọn size / Mua hàng' not in s:raise RuntimeError('Thieu nut chon size')
    notice='    <div class="alert bad" role="status" th:if="${param[\'phien-het-han\'] != null}">Phiên tài khoản trước đã kết thúc. Bạn có thể tiếp tục mua hàng không cần đăng nhập. Hãy chọn lại sản phẩm.</div>\n'
    if notice not in s:
        anchor='<div th:fragment="alerts" class="container alerts">\n'
        s=once(s,anchor,anchor+notice,'thong bao het phien')
    return s

def stage_repair(staged, reference, patch):
    pom=read(staged,'pom.xml')
    if '<artifactId>mens-store</artifactId>' not in pom or '<version>2.1.1</version>' not in pom:raise RuntimeError('Chi ho tro MENS STORE 2.1.1')
    email_login='findAuthenticatedAccount(' in read(staged,J+'service/CustomerAccountService.java')
    for name in MODULE_JAVA:
        path=J+name;s=read(reference,path)
        if not email_login:s=s.replace('customers.findAuthenticatedAccount(auth)','customers.findByPhone(auth.getName())')
        put(staged,path,s)
    for path in MODULE_RES:put(staged,path,read(reference,path))
    path='src/test/java/com/example/mens_store/service/DirectOrderTest.java'
    s=read(reference,path)
    if not email_login:s=s.replace('customers.findAuthenticatedAccount(auth)','customers.findByPhone(auth.getName())')
    put(staged,path,s)
    path=J+'config/SecurityConfig.java';put(staged,path,repair_security(read(staged,path)))
    path=J+'config/CustomerSessionFilter.java';put(staged,path,repair_filter(read(staged,path)))
    path=T+'home.mens.html';put(staged,path,repair_home(read(staged,path),patch))
    path=T+'fragments.html';put(staged,path,repair_fragments(read(staged,path),patch))
    path=T+'admin/order.html';s=read(staged,path)
    if 'line.sizeLabel()' not in s:
        s=once(s,'<th>Trang phục / phụ kiện</th><th>Số lượng</th>','<th>Trang phục / phụ kiện</th><th>Size đã chọn</th><th>Số lượng</th>',path)
        s=once(s,'<td th:text="${line.productName()}">Tên sản phẩm thời trang</td>','<td th:text="${line.productName()}">Tên sản phẩm thời trang</td>\n              <td th:text="${line.sizeLabel()}">M</td>',path)
    put(staged,path,s)
    path=T+'customer/login.html';s=read(staged,path)
    if 'Tiếp tục mua hàng không cần tài khoản' not in s:
        anchor='    <p class="auth-admin-link">'
        s=once(s,anchor,'    <p class="auth-switch"><a class="btn btn-outline block" th:href="@{/san-pham}">Tiếp tục mua hàng không cần tài khoản →</a></p>\n'+anchor,path)
    put(staged,path,s)
    # Guard against the original JS/backend login locks and verify that the restored
    # module contains size selection, CSRF, a guest cart and an owned guest receipt.
    js=read(staged,A+'js/home-store.js')
    if 'requestLogin(' in js or 'if (!loggedIn)' in js:raise RuntimeError('JavaScript van con khoa dang nhap cu')
    detail=read(staged,T+'detail.html')
    for token in ('name="size"','/dat-hang/mua-ngay/bat-dau','/gio-hang/them','${_csrf.token}'):
        if token not in detail:raise RuntimeError('Thieu '+token+' o trang chi tiet')
    if 'MS_GUEST_SIZED_CART' not in read(staged,J+'service/CartService.java'):raise RuntimeError('Thieu gio vang lai')
    if 'MS_GUEST_RECEIPTS' not in read(staged,J+'controller/CheckoutSupport.java'):raise RuntimeError('Thieu kiem tra phien don vang lai')

def extract_zip(data, dest, include):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if not include(name) or name.endswith('/'):continue
            p=dest/name
            if not p.resolve().is_relative_to(dest.resolve()):raise RuntimeError('ZIP path invalid')
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))

def main():
    repo=Path(capture('git','-C',sys.argv[1] if len(sys.argv)>1 else '/workspaces/mens-store','rev-parse','--show-toplevel').decode().strip()).resolve()
    ref=capture('git','-C',str(repo),'rev-parse',sys.argv[2] if len(sys.argv)>2 else 'FETCH_HEAD').decode().strip()
    def gitfile(path):return capture('git','-C',str(repo),'show',ref+':'+path)
    project=find_project(repo);print('Thu muc web dang dung:',project,flush=True)
    with tempfile.TemporaryDirectory(prefix='mens-store-guest-repair-') as d:
        work=Path(d);reference=work/'reference';reference.mkdir();initial=work/'initial';staged=work/'staged';home=work/'backup';home.mkdir()
        shutil.copytree(project/'src',initial/'src');shutil.copytree(initial/'src',staged/'src')
        shutil.copy2(project/'pom.xml',staged/'pom.xml')
        # Construct an exact clean reference from committed files, never patch the live files line-by-line.
        original=gitfile('mens-store-hoan-chinh.zip')
        if hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()!='933e526a31c252a1838e7a989016a7ce930cf557':raise RuntimeError('ZIP goc khong dung ban')
        extract_zip(original,reference,lambda n:n.startswith('src/') or n in ('pom.xml','compose.yaml'))
        premium=gitfile('cap-nhat-giao-dien/mens-store-cap-nhat-giao-dien.zip')
        if hashlib.sha256(premium).hexdigest()!='ceea426298b4dd8decf1e8e92b50cd291fd390c92a4ece85cf22dbb3e83454e2':raise RuntimeError('ZIP giao dien sai checksum')
        extract_zip(premium,reference,lambda n:n.startswith('src/'))
        prepare_reference(reference)
        env={**os.environ,'HOME':str(home)}
        for folder in ('cap-nhat-mua-ngay','cap-nhat-ton-kho','cap-nhat-bang-size'):
            script=work/'prerequisite.py';script.write_bytes(gzip.decompress(gitfile(folder+'/apply.py.gz')))
            print('Tao ban tham chieu:',folder,flush=True);cmd(sys.executable,'-E',str(script),str(reference),env=env)
        payload=b''.join(gitfile('cap-nhat-size-khach/patch.part'+str(i)) for i in range(1,5));checksum='d59b67503c34af2f9ec1976f49aadcffd8d16fee06f8375f2448c176970bc89c'
        if hashlib.sha256(payload).hexdigest()!=checksum:raise RuntimeError('Goi chon size sai checksum')
        patch=json.loads(gzip.decompress(payload));patchfile=work/'patch.json.gz';patchfile.write_bytes(payload)
        script=work/'guest.py';script.write_bytes(gitfile('cap-nhat-size-khach/apply.py'))
        cmd(sys.executable,'-E',str(script),str(reference),str(patchfile),checksum,env=env)
        stage_repair(staged,reference,patch)
        if shutil.which('node'):cmd('node','--check',str(staged/A/'js/home-store.js'))
        sync=work/'sync.py';sync.write_bytes(gitfile('cap-nhat-mua-khong-tai-khoan/sync.py'))
        cmd(sys.executable,'-E',str(sync),str(project),str(staged),str(initial))
        # Rebuild the actual active project's container; do not touch MySQL's volume.
        cmd('docker','compose','build','web',cwd=project)
        cmd('docker','compose','up','-d','--no-deps','--force-recreate','web',cwd=project)
        cmd('docker','compose','ps',cwd=project)
        verify=work/'verify.py';verify.write_bytes(gitfile('cap-nhat-mua-khong-tai-khoan/verify.py'))
        cmd(sys.executable,'-E',str(verify),cwd=project)

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('CAP NHAT CHUA THANH CONG:',str(e),file=sys.stderr);sys.exit(1)
