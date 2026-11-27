#!/usr/bin/env python3
"""Separate adding to cart from buying in MENS STORE 2.1.1."""
from pathlib import Path
import sys, tempfile, shutil, os

root = Path(sys.argv[1] if len(sys.argv) > 1 else '/workspaces/mens-store/mens-store').resolve()
if not (root/'pom.xml').is_file() or not (root/'compose.yaml').is_file():
    raise SystemExit('Khong tim thay du an: ' + str(root))
T = 'src/main/resources/templates/'
A = 'src/main/resources/static/assets/'
J = 'src/main/java/com/example/mens_store/controller/'
pending = {}

def replace(path, old, new):
    s = pending[path] if path in pending else (root/path).read_text(encoding='utf-8')
    if new in s:
        return
    if s.count(old) != 1:
        raise SystemExit('Khong khop phien ban: ' + path + '. Chua ghi file nao.')
    pending[path] = s.replace(old, new, 1)

def add_file(path, content):
    if (root/path).is_file():
        if (root/path).read_text(encoding='utf-8') != content:
            raise SystemExit('File da ton tai va co noi dung khac: ' + path)
    else:
        pending[path] = content

# Add is a cart operation only, not an order operation. Fixed redirect, no user-supplied URL.
replace(J+'CartController.java', '''    public String add(@RequestParam int id,@RequestParam(defaultValue="1") int quantity,HttpSession session,RedirectAttributes flash){
        try{cart.add(session,id,quantity);flash.addFlashAttribute("message","Đã thêm vào giỏ hàng");}
        catch(IllegalArgumentException | ArithmeticException ex){flash.addFlashAttribute("error",ex.getMessage());}
        return "redirect:/gio-hang";
    }''', '''    public String add(@RequestParam int id,@RequestParam(defaultValue="1") int quantity,
            @RequestParam(defaultValue="false") boolean stayOnDetail,
            HttpSession session,RedirectAttributes flash){
        try {
            cart.add(session,id,quantity);
            flash.addFlashAttribute("message","Đã thêm vào giỏ hàng. Bạn có thể tiếp tục chọn sản phẩm.");
            if (stayOnDetail) return "redirect:/san-pham/" + id;
        } catch (IllegalArgumentException | ArithmeticException ex) {
            flash.addFlashAttribute("error",ex.getMessage());
        }
        return "redirect:/gio-hang";
    }''')

p=T+'detail.html'
replace(p, '<main class="container detail-layout">', '<main class="container detail-layout purchase-detail">')
replace(p, '    <form th:action="@{/gio-hang/them}" method="post" class="buy-form">', '''    <section class="purchase-add-box" aria-label="Chọn sản phẩm">
      <p class="purchase-kicker">01 / CHỌN SẢN PHẨM</p>
      <h2>Thêm vào giỏ hàng</h2>
      <form th:action="@{/gio-hang/them}" method="post" class="buy-form">
      <input type="hidden" name="stayOnDetail" value="true">''')
replace(p, '<input type="number" name="quantity" class="input" min="1" th:max="${product.stock()}" value="1">', '<input type="number" name="quantity" class="input" min="1" th:max="${T(java.lang.Math).min(99, product.stock())}" value="1" required th:disabled="${product.stock() == 0}">')
replace(p, '''    </form>
    <p class="note">Giỏ hàng được lưu trong tài khoản MENS STORE. Đăng nhập để giữ những món đồ bạn đang cân nhắc.</p>''', '''      </form>
      <p class="purchase-note">Thêm vào giỏ chưa tạo đơn hàng và chưa cần nhập địa chỉ nhận hàng.</p>
      <div class="purchase-links">
        <a class="btn btn-outline" th:href="@{/gio-hang}">Xem giỏ hàng (<span th:text="${cartCount}">0</span>) →</a>
        <a class="link" th:href="@{/san-pham}">← Tiếp tục mua sắm</a>
      </div>
      <p class="note" th:unless="${customerLoggedIn}">Vui lòng đăng nhập Gmail/email tài khoản MENS STORE để lưu giỏ hàng.</p>
    </section>''')

# Show the actual shopping stages; only the checkout page contains the shipping form.
def steps(current):
    labels=['Giỏ hàng','Thông tin &amp; thanh toán','Xác nhận đơn hàng']
    return '<nav class="purchase-steps" aria-label="Quy trình mua hàng">' + ''.join(
        '<span class="purchase-step'+(' is-current' if i==current else '')+'"'+(' aria-current="step"' if i==current else '')+'><b>'+str(i)+'</b>'+label+'</span>' for i,label in enumerate(labels,1))+'</nav>'

p=T+'cart.html'
replace(p, '<h1>Những món đồ bạn đã chọn</h1>', '<h1>Giỏ hàng của bạn</h1>')
replace(p, '<p>Xem lại áo, quần và phụ kiện trước khi hoàn thiện đơn hàng.</p>', '<p>Kiểm tra sản phẩm, điều chỉnh số lượng và chỉ mua khi bạn đã sẵn sàng.</p>')
replace(p, '<main class="container section">', '<main class="container section purchase-cart">\n  '+steps(1))
replace(p, '<a class="btn btn-orange block" th:href="@{/dat-hang}">Nhập thông tin nhận hàng →</a>', '<a class="btn btn-orange block purchase-primary" th:href="@{/dat-hang}">Mua hàng →</a>')
replace(p, 'Giá và số lượng còn lại được kiểm tra khi đặt hàng. Những món chưa mua vẫn được lưu riêng trong tài khoản MENS STORE của bạn.', 'Bạn chưa đặt hàng. Bấm Mua hàng để nhập địa chỉ nhận hàng và chọn thanh toán. Đơn hàng chỉ được tạo khi bạn xác nhận ở bước cuối.')

p=T+'checkout.html'
replace(p, '<h1>Hoàn thiện đơn hàng của bạn</h1>', '<h1>Thanh toán và đặt hàng</h1>')
replace(p, '<main class="container section">', '<main class="container section purchase-checkout">\n  '+steps(2))
replace(p, '<h2>Gửi trang phục đến người nhận</h2>', '<h2>Thông tin nhận hàng</h2>')
replace(p, '<button type="submit" class="btn btn-orange block">Đặt hàng tại MENS STORE →</button>', '<button type="submit" class="btn btn-orange block purchase-primary">Xác nhận đặt hàng →</button>')
replace(p, 'Bạn có thể xem lại đơn trong tài khoản. Với chuyển khoản, cửa hàng xác nhận thanh toán sau khi kiểm tra số tiền đã nhận.', 'Chỉ khi bấm Xác nhận đặt hàng, hệ thống mới tạo đơn. Với chuyển khoản, cửa hàng xác nhận thanh toán sau khi kiểm tra số tiền đã nhận.')

# The mini cart must go to the full cart instead of jumping to checkout.
replace(T+'home.mens.html', '                Tiếp tục đặt hàng\n', '                Xem giỏ hàng\n')
replace(A+'js/home-store.js', "        window.location.href = '/dat-hang';", "        window.location.href = '/gio-hang';")
replace(T+'fragments.html', '<link rel="stylesheet" th:href="@{/assets/css/style.css}">', '<link rel="stylesheet" th:href="@{/assets/css/style.css}">\n    <link rel="stylesheet" th:href="@{/assets/css/purchase-flow.css}">')

add_file(A+'css/purchase-flow.css', '''/* MENS STORE: isolated product, cart and checkout styles */
.purchase-add-box{padding:22px;margin:20px 0;border:1px solid #e5ded5;border-radius:18px;background:#fff;box-shadow:0 8px 28px #20232608}
.purchase-kicker{font-size:11px;font-weight:800;letter-spacing:.12em;color:#ac5f39;margin:0 0 7px}
.purchase-add-box h2{font-size:21px;margin:0 0 12px}
.purchase-add-box .buy-form{display:flex;align-items:end;gap:12px;margin:16px 0}
.purchase-add-box .buy-form .btn{flex:1;min-height:46px}
.purchase-add-box .buy-form label{min-width:84px;max-width:105px}
.purchase-add-box .buy-form input{width:100%}
.purchase-note{font-size:13px;line-height:1.5;color:#5a625c;background:#f4f0e9;border-radius:10px;padding:12px}
.purchase-links{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:15px}
.purchase-steps{display:flex;align-items:center;gap:10px;margin:0 0 26px;padding:14px;border:1px solid #e5ded5;border-radius:15px;background:#fff;flex-wrap:wrap}
.purchase-step{display:flex;align-items:center;gap:9px;flex:1;min-width:155px;padding:10px 12px;border-radius:10px;font-size:13px;font-weight:700;color:#747972}
.purchase-step b{display:grid;place-items:center;flex:0 0 28px;height:28px;background:#eeeae3;border-radius:50%;color:#424846}
.purchase-step.is-current{background:#f5e9dc;color:#6d3c23}
.purchase-step.is-current b{background:#bd693d;color:#fff}
.purchase-cart .panel,.purchase-checkout .panel{border-radius:18px}
.purchase-cart .cart-row>img{width:93px;height:100px;object-fit:cover}
.purchase-cart .order-box,.purchase-checkout .order-box{box-shadow:0 10px 32px #2023260d}
.purchase-primary{min-height:48px;font-weight:800;text-align:center}
.purchase-checkout .payment-method{border:1px solid #eadbd0;background:#faf6f1}
.purchase-checkout .payment-method input[type=radio]{accent-color:#b9663f}
@media(max-width:760px){.purchase-add-box{padding:15px}.purchase-steps{gap:4px;padding:8px}.purchase-step{min-width:110px;padding:8px;font-size:11px}.purchase-cart .cart-row>img{width:64px;height:76px}.purchase-links{gap:10px}.purchase-add-box .buy-form .btn{min-width:0;white-space:normal}}
''')

# Validate all anchors before modifying files, and preserve previous admin/image work.
if not pending:
    print('Da cap nhat, khong can ghi lai.')
    raise SystemExit(0)
backup=Path(tempfile.mkdtemp(prefix='mens-store-purchase-backup-',dir=Path.home()))
for path in pending:
    if (root/path).is_file():
        dest=backup/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/path,dest)
print('Sao luu:',backup)
written=[]
try:
    for path,content in pending.items():
        p=root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        tmp=p.with_name(p.name+'.purchase-update.tmp')
        tmp.write_text(content,encoding='utf-8')
        if p.exists(): shutil.copymode(p,tmp)
        os.replace(tmp,p)
        written.append(path)
        print('OK:',path)
except Exception:
    for path in reversed(written):
        if (backup/path).is_file(): shutil.copy2(backup/path,root/path)
        else: (root/path).unlink(missing_ok=True)
    raise
print('Hoan tat. Khong thay doi SQL, .env, du lieu gio hang hay don hang.')
