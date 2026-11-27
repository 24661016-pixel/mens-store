# Nâng cấp quản trị MENS STORE

Dùng cho MENS STORE 2.1.1 bản gốc, Gmail và Premium. Phần quản trị đã có dashboard, quản lý đơn hàng, thêm/sửa sản phẩm, danh mục và khách hàng. Bản này thêm lối vào Quản trị, nút xóa sản phẩm an toàn, giao diện quản lý sản phẩm/danh mục, cho phép sửa sản phẩm ở danh mục đã ẩn và bỏ liên kết danh mục ẩn trên cửa hàng.

Xóa sản phẩm chỉ khi không có đơn hàng, giỏ hàng hoặc bình luận tham chiếu. Nếu có dữ liệu liên quan, dùng Ẩn sản phẩm. Chỉ xóa danh mục trống. Bảo vệ các đường dẫn /quan-tri bằng ROLE_ADMIN như mã nguồn cũ. Không thay đổi SQL, .env, volume MySQL, ảnh sản phẩm hoặc đăng nhập khách.

## Áp dụng trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:cap-nhat-quan-tri/apply.py > /tmp/mens-store-admin.py && python3 /tmp/mens-store-admin.py /workspaces/mens-store/mens-store && cd /workspaces/mens-store/mens-store && docker compose build web && docker compose up -d --no-deps web

Đăng nhập /quan-tri bằng APP_ADMIN_USERNAME (thường là admin) và APP_ADMIN_PASSWORD đã đặt trong .env. Không gửi mật khẩu cho người khác. Script sao lưu các file sẽ sửa trong thư mục HOME; nếu không khớp phiên bản thì dừng trước khi ghi. Sau khi build thành công, tải lại trang bằng Ctrl+F5.

Kiểm tra: thêm, sửa, ẩn/hiện, xóa sản phẩm thử chưa có dữ liệu; ẩn/hiện danh mục; kiểm tra trang khách; xác nhận tài khoản khách không thể vào /quan-tri. Không xóa volume database.
