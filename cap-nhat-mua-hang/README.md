# MENS STORE — Giỏ hàng và mua hàng riêng biệt

- Trang chi tiết: chọn số lượng, thêm vào giỏ, ở lại trang chi tiết sau khi thêm thành công; không tạo đơn, không yêu cầu địa chỉ giao hàng.
- Giỏ hàng: xem, cập nhật số lượng, xóa sản phẩm, tạm tính, bấm Mua hàng khi sẵn sàng.
- Thanh toán: chỉ tại /dat-hang mới có thông tin giao hàng, chọn COD hoặc chuyển khoản nếu được cấu hình; chỉ POST xác nhận đặt hàng mới tạo đơn.
- Giỏ hàng thu nhỏ trên trang chủ dẫn tới /gio-hang thay vì /dat-hang.
- Giữ phân quyền, đăng nhập Gmail, admin, ảnh, SQL, .env và dữ liệu MySQL.

## Áp dụng trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:cap-nhat-mua-hang/apply.py > /tmp/mens-store-mua-hang.py && python3 /tmp/mens-store-mua-hang.py /workspaces/mens-store/mens-store && cd /workspaces/mens-store/mens-store && docker compose build web && docker compose up -d --no-deps web

Script kiểm tra các đoạn mã trước khi thay đổi 8 file, sao lưu trong HOME, không git pull, không xóa dữ liệu. Đã thử áp dụng trên ZIP gốc và Premium, chạy lại không thay đổi thêm, kiểm tra cú pháp Python và JavaScript. Chưa kiểm thử ứng dụng Spring Boot/MySQL đang chạy trong Codespaces. Sau khi build thành công, nhấn Ctrl+F5 rồi kiểm tra chi tiết, thêm giỏ, xem giỏ, thanh toán. Nếu chỉ kiểm tra giao diện, không bấm xác nhận đơn hàng thật.
