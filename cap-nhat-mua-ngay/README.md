# MENS STORE — Mua ngay độc lập với giỏ hàng

- Trang chi tiết có hai nút: Thêm vào giỏ hàng và Mua ngay.
- Giỏ hàng là danh sách sản phẩm đã lưu. Bấm tên/ảnh để xem chi tiết; mỗi dòng đủ tồn kho có nút Mua ngay mẫu này.
- Mua ngay tạo đơn riêng theo mẫu và số lượng đang chọn. Không thêm vào, đọc hay xóa giỏ hàng khi tạo đơn trực tiếp.
- Sản phẩm ngừng bán vẫn hiển thị trong giỏ nếu đã lưu nhưng không thể mua.
- Chỉ khách hàng đã đăng nhập có thể thanh toán; giá và tồn kho được kiểm tra lại trên server khi đặt hàng.
- Giữ nguyên phân quyền quản trị, SQL, .env và ảnh. Luồng thanh toán cả giỏ cũ vẫn được giữ ở backend để tương thích.

## Cập nhật trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:cap-nhat-mua-ngay/apply.py.gz > /tmp/mens-store-mua-ngay.py.gz && gzip -dc /tmp/mens-store-mua-ngay.py.gz > /tmp/mens-store-mua-ngay.py && python3 /tmp/mens-store-mua-ngay.py /workspaces/mens-store/mens-store && cd /workspaces/mens-store/mens-store && docker compose build web && docker compose up -d --no-deps web

Gói cập nhật nén chứa mã Python, SHA-256 mã giải nén: ab428c927772406562a475a471507eedcfe5bbe1d64e120f152df6343f51fc0e.
Mã cập nhật kiểm tra phiên bản, sao lưu file trước khi ghi, và có thể chạy lại. Đã thử áp dụng trên ZIP Premium và các bản nguồn đã áp dụng cập nhật mua hàng trước. Kiểm tra cú pháp Python và JavaScript thành công. Có bổ sung kiểm thử Java về việc mua trực tiếp không đọc/xóa giỏ; chưa chạy kiểm thử Maven hoặc ứng dụng MySQL thực tế vì môi trường kiểm tra không có Maven/Docker.

## Kiểm tra sau cập nhật

Đăng nhập khách hàng. Thêm A vào giỏ, mở B và mua ngay B. Kiểm tra màn hình xác nhận chỉ có B. Nếu tạo đơn thử, kiểm tra giỏ vẫn có A và không tự thêm B. Thử mua riêng một dòng trong giỏ, sau đó kiểm tra giỏ vẫn giữ các món đã lưu. Không đặt đơn thật nếu chỉ muốn kiểm tra giao diện.
