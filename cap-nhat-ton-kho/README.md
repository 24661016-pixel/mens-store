# MENS STORE — Hiển thị tồn kho và chọn số lượng

- Trang chủ, bộ sưu tập, chi tiết, giỏ hàng: hiển thị số lượng tồn kho từ dữ liệu MySQL khi tải trang.
- Trên 10: Còn hàng; 1–10: Sắp hết; 0: Hết hàng. Nút thêm giỏ và mua ngay vẫn bị khóa khi hết hàng.
- Nút tăng/giảm và tạm tính theo số lượng đang chọn. Giới hạn 1 đến min(99, tồn kho), đồng thời giữ kiểm tra ở backend.
- Quản trị: cảnh báo màu ở danh sách sản phẩm, đồng bộ ngưỡng 1–10 ở báo cáo tồn kho và AI.
- Không sửa số lượng tồn hiện tại, SQL, mật khẩu, .env, tài khoản, ảnh, giỏ hàng hoặc lịch sử đơn. Giữ xử lý trừ kho khi tạo đơn và hoàn kho khi hủy hợp lệ đã có trong OrderService.

## Áp dụng trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:cap-nhat-ton-kho/apply.py.gz > /tmp/mens-store-ton-kho.py.gz && gzip -dc /tmp/mens-store-ton-kho.py.gz > /tmp/mens-store-ton-kho.py && python3 /tmp/mens-store-ton-kho.py /workspaces/mens-store/mens-store && cd /workspaces/mens-store/mens-store && docker compose build web && docker compose up -d --no-deps web

Nếu chưa áp dụng bản Mua ngay, hãy áp dụng bản cap-nhat-mua-ngay trước. Script tồn kho cũng chạy được trên bản gốc, nhưng không tự cài đặt chức năng Mua ngay.
Script kiểm tra cấu trúc và các đoạn mã trước khi ghi, sao lưu trong HOME, có thể chạy lại. SHA-256 của mã Python giải nén: 2f5c594dd8e4c25d91783b630a06a470626598512c3db41b8577935c9b36cf7c.

## Kiểm tra
Đã kiểm tra áp dụng 10 file trên bản gốc và Premium, gồm bản Premium đã áp dụng Mua ngay lấy từ GitHub; kiểm tra chạy lại và cú pháp Python/JS; mô phỏng JavaScript tăng/giảm, tạm tính, tồn kho 0, 1, 25, 200, nhập sai hoặc vượt giới hạn. Chưa chạy Spring Boot/Maven/MySQL thực tế. Sau build, Ctrl+F5. Kiểm tra bằng cách sửa tồn kho của sản phẩm thử trong quản trị thành 25, 5, 0, mở lại chi tiết; xác nhận số lượng và nút mua đúng, rồi khôi phục tồn kho thử nghiệm. Không cần xóa database.
