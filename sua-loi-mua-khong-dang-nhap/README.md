# MENS STORE – Khôi phục mua hàng vãng lai v3

Bản sửa cho trường hợp Mua ngay/Thêm giỏ vẫn chuyển đến đăng nhập, hoặc các bản cập nhật trước bị dừng do khác phiên bản. Sửa SecurityConfig, CustomerSessionFilter, frontend; phục hồi đồng bộ các lớp xử lý giỏ hàng, chọn size, mua trực tiếp và thanh toán vãng lai từ bộ mã tham chiếu 2.1.1. Giữ đăng nhập Gmail hoặc điện thoại tùy phiên bản đang chạy; quyền ADMIN và tài khoản vẫn được bảo vệ, CSRF không bị tắt. Khách mua trực tiếp không cần đăng ký, không thay đổi giỏ, chọn size trước khi mua. 

## Chạy trong Codespaces

    cd /workspaces/mens-store
    git fetch origin main && git show FETCH_HEAD:sua-loi-mua-khong-dang-nhap/repair.py > /tmp/mens-store-fix-guest.py && python3 /tmp/mens-store-fix-guest.py /workspaces/mens-store FETCH_HEAD

Tự xác định thư mục dự án từ container web đang chạy (hoặc thư mục hợp lệ duy nhất), dựng bản tham chiếu từ ZIP và các bản cập nhật đã commit, kiểm checksum, sửa trên bản sao, sao lưu các file thay đổi trong HOME, thay lại các file module mua hàng bằng phiên bản đồng bộ. Những tùy chỉnh riêng trong các file module mua hàng được thay thế; có thể lấy lại từ backup. Giữ trang chủ, navbar, phần admin ngoài chi tiết đơn, ảnh, cấu hình đăng nhập, .env, SQL và volume. Nếu không nhận diện được cấu trúc nguồn, dừng trước khi ghi file. Tự build và force-recreate đúng dịch vụ web, kiểm tra luồng mua hàng bằng phiên HTTP chưa đăng nhập. Yêu cầu DB đang chạy; SizeSchema tự bổ sung bảng giỏ theo size và cột kích cỡ nếu chưa có, không xóa dữ liệu. Không tạo đơn hàng thật trong bước kiểm tra.

Kiểm tra cục bộ đã thực hiện: cú pháp Python; sửa phân quyền và xử lý phiên cũ trên cả ZIP gốc và Premium Gmail; dựng lại 5 file Java đầu vào tham chiếu Gmail khớp từng byte với bản Premium. Chưa chạy toàn bộ trình cài trong Codespaces, chưa chạy Spring Boot/MySQL hoặc xác nhận checkout thực tế. Kết quả trực tiếp được in khi chạy lệnh: KIEM TRA THANH CONG hoặc lỗi CAP NHAT CHUA THANH CONG / KIEM TRA CHUA DAT. Nếu lỗi, gửi các dòng lỗi cuối; không chạy docker compose down -v và không gửi mật khẩu.
