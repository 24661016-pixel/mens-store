# MENS STORE – Chọn size và mua không cần tài khoản

- Áo/quần: chọn size bằng nút radio theo bảng size của mẫu; phụ kiện dùng lựa chọn Theo mẫu. Bảng số đo và size là tham khảo, cửa hàng xác nhận trước khi giao.
- Khách vãng lai có thể thêm giỏ, mua ngay, nhập thông tin nhận hàng và chọn COD hoặc chuyển khoản nếu cửa hàng đã cấu hình. Không yêu cầu tạo tài khoản, Gmail không bắt buộc.
- Giỏ khách lưu theo phiên trình duyệt (có thể mất khi hết phiên hoặc khởi động lại máy chủ), giỏ khách và giỏ tài khoản không tự gộp. Đơn vẫn được lưu trong MySQL.
- Mỗi size là một dòng riêng trong giỏ và đơn. Khách có thể đổi size bằng danh sách chọn. Dòng giỏ cũ chưa có size được giữ nguyên, khách chọn size trước khi đặt. Mua ngay không xóa giỏ.
- Kiểm tra size trên server, tổng tồn kho theo sản phẩm (chưa có tồn kho riêng từng size). Giữ cơ chế giao dịch trừ kho, hoàn kho khi hủy hợp lệ.
- Quản trị xem size đã chọn trong chi tiết đơn. Không nới quyền /quan-tri, /tai-khoan hoặc bình luận. Giữ CSRF và token chống gửi đơn lặp. Khách xem xác nhận đơn trong phiên đã đặt, không mở thông tin người khác qua mã đơn.
- Khi ứng dụng khởi động, SizeSchema tự CREATE TABLE IF NOT EXISTS gio_hang_kich_co và thêm cột kich_co vào chi_tiet_don_hang nếu chưa có. Đây là thay đổi cộng thêm, không xóa hay ghi đè dữ liệu cũ. Tài khoản DB phải có quyền CREATE và ALTER. Sao lưu DB trước khi đưa vào môi trường thật. Không xóa volume.

## Cập nhật trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:cap-nhat-size-khach/apply.sh > /tmp/mens-store-size-khach.sh && bash /tmp/mens-store-size-khach.sh /workspaces/mens-store/mens-store FETCH_HEAD

Script ghép 4 phần của gói nén, kiểm SHA-256, áp dụng các cập nhật trước nếu thiếu, kiểm nội dung 27 file trước khi ghi, sao lưu trong HOME, build và khởi động lại chỉ dịch vụ web. Nếu mã nguồn khác phiên bản, dừng an toàn và báo file không khớp; các cập nhật điều kiện đã chạy thành công trước đó vẫn được giữ.

## Kiểm tra

Đã thử cài trên bản Premium với Mua ngay/tồn kho/bảng size và cài lần lượt các điều kiện từ ZIP Premium, chạy lại không ghi đè thêm, thử giữ tùy chỉnh navbar/CSS admin, kiểm cú pháp Python và JavaScript. Biên dịch Java 21 các model và lớp xử lý CartService, OrderService, CheckoutSupport với test doubles, chạy mô phỏng chọn size, giỏ khách độc lập, đổi size, giới hạn tồn, mua trực tiếp không xóa giỏ và bảo vệ xác nhận đơn. Có bổ sung test Java dùng Mockito trong dự án. Chưa chạy Maven, Spring Boot, Thymeleaf, MySQL hay Docker thực tế.

Sau build, mở cửa sổ ẩn danh, chọn size áo/quần, thêm 2 size vào giỏ, bấm Mua ngay, kiểm thông tin giao hàng và tạm tính. Nếu đặt đơn thử, dùng COD và thông tin thử nghiệm, lưu mã đơn, kiểm size từng dòng trong admin rồi hủy đơn thử nếu phù hợp. Kiểm tra phiên khác không mở được trang xác nhận đơn khách và khách không vào được quản trị. Không dùng dữ liệu cá nhân thật khi thử nghiệm.
