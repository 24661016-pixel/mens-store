#!/usr/bin/env python3
"""Update MENS STORE admin features in an existing extracted 2.1.1 project."""
from pathlib import Path
import sys, tempfile, shutil, os

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspaces/mens-store/mens-store").resolve()
if not (root / "pom.xml").is_file() or not (root / "compose.yaml").is_file():
    raise SystemExit("Khong tim thay du an: " + str(root))
j = "src/main/java/com/example/mens_store/"
t = "src/main/resources/templates/"
pending = {}

def read(path):
    return pending[path] if path in pending else (root / path).read_text(encoding="utf-8")

def replace(path, old, new):
    text = read(path)
    if new in text:
        return
    if text.count(old) != 1:
        raise SystemExit("Khong khop phien ban: " + path + ". Chua ghi bat ky file nao.")
    pending[path] = text.replace(old, new, 1)

def add_file(path, content):
    p = root / path
    if p.exists():
        if read(path) != content:
            raise SystemExit("File da co noi dung khac: " + path)
    else:
        pending[path] = content

if '.requestMatchers("/quan-tri", "/quan-tri/**").hasRole("ADMIN")' not in read(j + "config/SecurityConfig.java"):
    raise SystemExit("Khong xac nhan duoc bao ve ADMIN. Chua thay doi du an.")

repo = j + "repository/ShopRepository.java"
ctrl = j + "controller/AdminController.java"
replace(repo, "    public Optional<Product> findById(int id) {", '''    /** Admin category selection includes hidden categories. */
    public List<Category> allCategories() {
        return jdbc.query("SELECT * FROM danh_muc ORDER BY thu_tu,danh_muc_id", (rs, n) ->
            new Category(rs.getInt("danh_muc_id"), rs.getString("ma_danh_muc"),
                rs.getString("ten_danh_muc"), rs.getString("mo_ta")));
    }

    public Optional<Product> findById(int id) {''')
for old in ('m.addAttribute("productForm", new ProductForm());',
            'm.addAttribute("productForm", ProductForm.from(p));',
            'm.addAttribute("productForm", f);'):
    replace(ctrl, old, 'm.addAttribute("productCategories", products.allCategories());\n        ' + old)
replace(ctrl, "|| products.categories().stream()", "|| products.allCategories().stream()")
replace(ctrl, '    @PostMapping("/san-pham/{id}/trang-thai")', '''    @PostMapping("/san-pham/{id}/xoa")
    public String deleteProduct(@PathVariable int id, RedirectAttributes flash) {
        int deleted = 0;
        try {
            deleted = jdbc.update(
                "DELETE FROM san_pham WHERE san_pham_id=? "
                + "AND NOT EXISTS (SELECT 1 FROM chi_tiet_don_hang WHERE san_pham_id=?) "
                + "AND NOT EXISTS (SELECT 1 FROM gio_hang WHERE san_pham_id=?) "
                + "AND NOT EXISTS (SELECT 1 FROM binh_luan WHERE san_pham_id=?)",
                id, id, id, id);
        } catch (DataIntegrityViolationException ex) {
            // Foreign keys also protect a reference created concurrently.
        }
        flash.addFlashAttribute(deleted == 1 ? "message" : "error",
            deleted == 1 ? "Đã xóa sản phẩm."
                : "Không thể xóa: sản phẩm không tồn tại hoặc đã có đơn hàng, giỏ hàng hay bình luận. Hãy chọn Ẩn sản phẩm để giữ dữ liệu.");
        return "redirect:/quan-tri/san-pham";
    }

    @PostMapping("/san-pham/{id}/trang-thai")''')
form = t + "admin/product-form.html"
replace(form, 'th:each="c : ${categories}"', 'th:each="c : ${productCategories}"')
replace(form, '<option value="0">Chọn danh mục phù hợp</option>', '<option value="0">Chọn danh mục (kể cả danh mục đang ẩn)</option>')

p = t + "admin/products.html"
replace(p, '<main class="container section">', '<main class="container section admin-catalog">')
replace(p, 'Tủ đồ của cửa hàng</h1>', 'Quản lý sản phẩm</h1>')
replace(p, '+ Thêm mẫu mới</a>', '+ Thêm sản phẩm</a>')
replace(p, 'Ngừng kinh doanh sẽ ẩn mẫu khỏi cửa hàng và giữ nguyên lịch sử đơn. Khi hiển thị lại, danh mục của mẫu cũng cần được bật.',
    'Ẩn sản phẩm sẽ giữ nguyên dữ liệu. Chỉ xóa vĩnh viễn sản phẩm chưa có đơn hàng, giỏ hàng hoặc bình luận. Khi hiển thị lại, danh mục cũng phải được bật.')
replace(p, '<td th:text="${p.active() ? \'Được phép hiển thị\' : \'Ngừng kinh doanh\'}">Trạng thái</td>',
    '<td><span class="admin-state" th:classappend="${p.active() ? \'is-active\' : \'is-hidden\'}" th:text="${p.active() ? \'Đang hoạt động\' : \'Đã ẩn\'}">Trạng thái</span></td>')
replace(p, '<td>\n            <a class="link" th:href="@{/quan-tri/san-pham/{id}/sua(id=${p.id()})}">',
    '<td class="admin-row-actions">\n            <a class="btn btn-small btn-outline" th:href="@{/quan-tri/san-pham/{id}/sua(id=${p.id()})}">')
replace(p, 'Sửa thông tin mẫu</a>', 'Sửa</a>')
replace(p, "p.active()?'Ngừng kinh doanh':'Hiển thị lại mẫu'", "p.active()?'Ẩn sản phẩm':'Hiện sản phẩm'")
replace(p, '''            </form>
          </td>
        </tr>''', '''            </form>
            <form method="post" th:action="@{/quan-tri/san-pham/{id}/xoa(id=${p.id()})}" onsubmit="return confirm('Xóa vĩnh viễn sản phẩm này?');">
              <button class="btn btn-small admin-delete" type="submit">Xóa</button>
            </form>
          </td>
        </tr>''')

c = t + "admin/categories.html"
replace(c, '<main class="container section">', '<main class="container section admin-catalog">')
replace(c, 'Phân nhóm tủ đồ nam</h1>', 'Quản lý danh mục sản phẩm</h1>')
replace(c, '+ Thêm nhóm trang phục</a>', '+ Thêm danh mục</a>')
replace(c, '<td th:text="${c.active()?\'Đang hiển thị\':\'Đã ẩn danh mục\'}"></td>',
    '<td><span class="admin-state" th:classappend="${c.active() ? \'is-active\' : \'is-hidden\'}" th:text="${c.active() ? \'Đang hoạt động\' : \'Đã ẩn\'}"></span></td>')
replace(c, '<td>\n            <a class="link" th:href="@{/quan-tri/danh-muc/{id}/sua(id=${c.id()})}">',
    '<td class="admin-row-actions">\n            <a class="btn btn-small btn-outline" th:href="@{/quan-tri/danh-muc/{id}/sua(id=${c.id()})}">')
replace(c, 'Sửa nhóm trang phục</a>', 'Sửa</a>')
replace(c, '<button class="btn btn-small" type="submit">Xóa danh mục trống</button>',
    '<button class="btn btn-small admin-delete" type="submit" onclick="return confirm(\'Xóa danh mục trống này?\');">Xóa</button>')

home = t + "home.mens.html"
replace(home, '<li class="nav-item"><a class="nav-link" href="#categories">Danh mục</a></li>',
    '''<li class="nav-item"><a class="nav-link" href="#categories">Danh mục</a></li>
                <li class="nav-item" th:unless="${customerLoggedIn}"><a class="nav-link" th:href="@{/quan-tri}"><i class="bi bi-shield-lock"></i> Quản trị</a></li>''')
replace(home, '<a th:href="@{/tai-khoan}">Tài khoản của tôi</a>',
    '''<a th:href="@{/tai-khoan}">Tài khoản của tôi</a>
            <a th:unless="${customerLoggedIn}" th:href="@{/quan-tri}">Đăng nhập quản trị</a>''')

# Use the already filtered categories for header/footer and premium promotional tiles.
advice = j + "controller/WebAdvice.java"
replace(advice, 'model.addAttribute("categories", shop.categories());',
    '''var visibleCategories = shop.categories();
        model.addAttribute("categories", visibleCategories);
        model.addAttribute("activeCategoryIds", visibleCategories.stream().map(c -> c.id()).toList());''')
for name, cid in (("edit-shirt", 2), ("edit-denim", 4)):
    old = '<a class="edit-tile ' + name + '"'
    if old in read(home):
        replace(home, old, old + ' th:if="${activeCategoryIds.contains(' + str(cid) + ')}"')
fr = t + "fragments.html"
replace(fr, '''<a th:href="@{/san-pham(danh_muc=1)}">Áo thun</a>
            <a th:href="@{/san-pham(danh_muc=2)}">Sơ mi</a>''',
    '''<a th:each="c : ${categories}" th:if="${c.code() == 'AO_THUN' or c.code() == 'SO_MI'}" th:href="@{/san-pham(danh_muc=${c.id()})}" th:text="${c.name()}">Danh mục</a>''')
replace(fr, '''<p><a th:href="@{/san-pham(danh_muc=5)}">Áo khoác &amp; trang phục mặc ngoài</a></p>
            <p><a th:href="@{/san-pham(danh_muc=6)}">Phụ kiện nam</a></p>''',
    '''<p th:each="c : ${categories}" th:if="${c.code() == 'AO_KHOAC' or c.code() == 'PHU_KIEN'}"><a th:href="@{/san-pham(danh_muc=${c.id()})}" th:text="${c.name()}">Danh mục</a></p>''')

for path in (fr, t + "admin/dashboard.html"):
    replace(path, '<link rel="stylesheet" th:href="@{/assets/css/style.css}">',
        '<link rel="stylesheet" th:href="@{/assets/css/style.css}">\n  <link rel="stylesheet" th:href="@{/assets/css/admin-center.css}">')
nav = t + "admin/nav.html"
for old, new in [('Tổng quan &amp; đơn hàng</a>', 'Tổng quan / Đơn hàng</a>'),
                 ('Sản phẩm thời trang</a>', 'Quản lý sản phẩm</a>'),
                 ('Danh mục trang phục</a>', 'Quản lý danh mục</a>'),
                 ('>Khách hàng</a>', '>Quản lý khách hàng</a>')]:
    replace(nav, old, new)
add_file("src/main/resources/static/assets/css/admin-center.css", '''/* MENS STORE admin center */
.adminnav {display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:12px;border:1px solid #e5dfd7;border-radius:14px;background:#fff}
.adminnav a {display:inline-flex;align-items:center;min-height:40px;padding:10px 14px;font-weight:700;color:#242a2b;border-radius:9px;background:#f4f1eb}
.adminnav a:hover,.adminnav a:focus-visible {color:#fff;background:#2c3031}
.adminnav form {margin-left:auto}
.admin-catalog .admin-actions {gap:12px;flex-wrap:wrap;padding-top:12px}
.admin-catalog .tablewrap {padding:0;border-radius:16px;border:1px solid #e4dfd8;box-shadow:0 8px 28px rgba(40,32,25,.045);background:#fff;overflow-x:auto}
.admin-catalog table {width:100%;min-width:850px;border-collapse:collapse}
.admin-catalog thead th {background:#f0ede7;color:#4c5656;font-size:12px;padding:15px 12px}
.admin-catalog tbody td {padding:15px 12px;vertical-align:middle}
.admin-catalog tbody tr:hover {background:#faf8f4}
.admin-catalog .table-img {width:64px;height:72px;border-radius:9px;object-fit:cover}
.admin-catalog .admin-row-actions {min-width:210px}
.admin-catalog .admin-row-actions form {display:inline-block;margin:3px 1px}
.admin-catalog .admin-row-actions .btn {min-height:32px;padding:7px 10px;font-size:12px}
.admin-catalog .admin-delete {color:#a52626;background:#fff3f1;border:1px solid #ebc3bc}
.admin-catalog .admin-delete:hover {background:#a52626;color:white}
.admin-state {display:inline-block;padding:6px 10px;font-size:12px;font-weight:700;border-radius:999px;white-space:nowrap}
.admin-state.is-active {color:#226044;background:#e6f3eb}
.admin-state.is-hidden {color:#6c5a46;background:#f0ebe2}
@media(max-width:760px){.adminnav{gap:6px;padding:8px}.adminnav a{padding:8px 10px;font-size:12px}.adminnav form{margin-left:0}}
''')

# All replacement anchors are checked before writing any file.
if not pending:
    print("Ban quan tri da duoc cap nhat.")
    raise SystemExit(0)
backup = Path(tempfile.mkdtemp(prefix="mens-store-admin-backup-", dir=Path.home()))
for path in pending:
    if (root / path).is_file():
        target = backup / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / path, target)
print("Sao luu:", backup)
written = []
try:
    for path, content in pending.items():
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_name(p.name + ".admin-update.tmp")
        tmp.write_text(content, encoding="utf-8")
        if p.exists():
            shutil.copymode(p, tmp)
        os.replace(tmp, p)
        written.append(path)
        print("OK:", path)
except Exception:
    for path in reversed(written):
        if (backup / path).is_file():
            shutil.copy2(backup / path, root / path)
        else:
            (root / path).unlink(missing_ok=True)
    raise
print("Hoan tat. Khong thay doi SQL, .env, tai khoan, don hang.")
