# MENS STORE — Bảng size theo sản phẩm

Bổ sung liên kết Xem bảng size & cách đo ở trang chi tiết và bảng kích cỡ riêng theo tên/danh mục/phom sản phẩm. Kiểm tra đủ 20 mẫu SP001–SP020 trong SQL: áo thun regular/oversize/relaxed, sơ mi Oxford/denim/linen, polo regular/slim, quần chino/jeans/cargo/short, bomber/hoodie/cardigan, thắt lưng/nón/túi. Sản phẩm mới thuộc loại đã nhận diện cũng có hướng dẫn; loại chưa nhận diện chỉ hiển thị cách kiểm tra kích cỡ.

Bảng số đo cơ thể S–XXL hoặc 28–36 là dữ liệu tham khảo minh họa, KHÔNG phải kích thước thực tế của từng mẫu hay biến thể còn hàng. Dữ liệu SQL chưa có các số đo đó. Phụ kiện có hướng dẫn riêng, không tự gán size quần áo. Khách ghi size mong muốn ở ghi chú khi đặt hàng, cửa hàng xác nhận trước khi giao. Chưa quản lý biến thể/tồn kho theo size; không sửa SQL hoặc luồng đặt hàng.

## Áp dụng trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:cap-nhat-bang-size/apply.py.gz > /tmp/mens-store-size.py.gz && gzip -dc /tmp/mens-store-size.py.gz > /tmp/mens-store-size.py && python3 /tmp/mens-store-size.py /workspaces/mens-store/mens-store && cd /workspaces/mens-store/mens-store && docker compose build web && docker compose up -d --no-deps web

Script kiểm tra đoạn mã trước khi ghi 6 file, sao lưu trong HOME, chạy lại an toàn. SHA-256 mã Python giải nén: 3a506d04cc72a2aaf51a172757bd0dff14d059e612c6fe8e9ae1202d12bff7f5. Không sửa ảnh, SQL, .env, tài khoản, giỏ hàng, tồn kho, đơn hàng. Đã thử áp dụng trên ZIP gốc có SHA Git khớp repository và bản Premium có Mua ngay/tồn kho, kiểm tra chạy lại, cú pháp Python, biên dịch Java 21 lớp Product và SizeGuide, kiểm tra đúng bảng cho đủ 20 mẫu SQL và hai trường hợp mẫu mới/chưa biết. Chưa chạy Spring Boot/MySQL/Docker thực tế hoặc kiểm tra render Thymeleaf trong Codespaces.

Sau khi build, Ctrl+F5, mở chi tiết áo thun, quần jeans, hoodie và các phụ kiện. Kiểm tra bảng, liên kết, các nút mua/giỏ hàng và số lượng như trước. Trước kinh doanh thật, thay dữ liệu tham khảo bằng số đo của từng mẫu và xác nhận size có hàng.
