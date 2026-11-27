# MENS STORE — Mua hàng không cần tài khoản (bản sửa v2)

Cho phép khách chưa đăng nhập mở giỏ, chọn size, Mua ngay, điền thông tin giao hàng, xác nhận COD/chuyển khoản đã cấu hình. Đăng nhập chỉ là tùy chọn. Đơn của khách lưu trong MySQL với tai_khoan_id NULL, size lưu theo dòng. Giỏ vãng lai riêng theo phiên; Mua ngay không đổi giỏ. Giữ CSRF, token xác nhận, quyền ADMIN, quyền xem đơn theo tài khoản hoặc phiên đã đặt.

Bản v2 xử lý phiên tài khoản đã hết hạn khi truy cập các trang mua sắm công khai: tiếp tục GET/HEAD với tư cách khách, không tự gửi lại POST; yêu cầu chọn lại nếu phiên hết hạn trong lúc thao tác. Thêm lối tiếp tục mua không cần tài khoản trên trang đăng nhập. Không nới quyền quản trị hoặc truy cập thông tin đơn của người khác.

## Cài trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:cap-nhat-mua-khong-tai-khoan/apply.sh > /tmp/mens-store-guest-v2.sh && bash /tmp/mens-store-guest-v2.sh /workspaces/mens-store/mens-store FETCH_HEAD

Bản cài thực hiện mọi cập nhật trong bản sao src, sau đó sao lưu và chỉ ghi file thay đổi nếu tất cả bước kiểm tra mã thành công. Kiểm tra ngữ cảnh HTML/JS khi giao diện có chỉnh sửa nhẹ; dừng nếu không xác định được đoạn cần đổi. Không ép ghi đè Java đã chỉnh khác phiên bản, không ghi .env hay file SQL, không xóa volume. Cơ chế SizeSchema đã có vẫn tự thêm bảng và cột cần thiết nếu chưa tồn tại. Build lại web rồi kiểm tra bằng phiên HTTP mới tại localhost:8080: giỏ, Mua ngay, form nhận hàng, size, thêm giỏ, bảo vệ admin. Không gửi POST xác nhận đặt đơn, không thanh toán. Nếu chỉ còn phụ kiện có hàng, kiểm tra size áo/quần được báo chưa xác nhận.

## Kiểm tra đã thực hiện

Đã chạy apply.py trên bản Premium có các bản cập nhật điều kiện, bản legacy đã cài chọn size và bản thay đổi nhẹ HTML; chạy lần hai không ghi thêm. Xác nhận sao chép source giữ SQL nguyên vẹn, kiểm cú pháp Python/JS/Bash, chạy test doubles Java cho nghiệp vụ giỏ/size/đơn khách, chạy kiểm thử HTTP với máy chủ mô phỏng. Môi trường chưa có Maven/Docker, không truy cập trực tiếp Codespaces, nên chưa xác nhận ứng dụng thật hoặc MySQL. Sau khi cài, xem dòng KIEM TRA THANH CONG hoặc lỗi KIEM TRA CHUA DAT; nếu lỗi gửi nội dung Terminal. Không chạy docker compose down -v.

Lưu ý cổng Codespaces đặt Private có thể yêu cầu đăng nhập GitHub để mở địa chỉ ngoài, khác với đăng nhập tài khoản MENS STORE.
