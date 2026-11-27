# Cập nhật giao diện MENS STORE

Bản cập nhật gồm 20 ảnh sản phẩm minh họa AI, banner, CSS và trang chủ cho phiên bản đăng nhập email/Gmail. ZIP chứa 25 tệp, không chứa SQL, .env hay cơ sở dữ liệu.

## Áp dụng vào Codespaces đang chạy

```bash
cd /workspaces/mens-store
git fetch origin main
git show FETCH_HEAD:cap-nhat-giao-dien/cap-nhat.sh > /tmp/mens-store-cap-nhat.sh
bash /tmp/mens-store-cap-nhat.sh /workspaces/mens-store/mens-store FETCH_HEAD
````

Script kiểm tra SHA-256, sao lưu resources vào thư mục trong HOME, cập nhật ảnh và CSS, và thay trang chủ nếu nhận diện được backend đăng nhập Gmail tương thích. Sau đó build lại dịch vụ web bằng Docker Compose, không xóa MySQL. Nếu đã tùy chỉnh giao diện, kiểm tra bản sao lưu trước khi thay thế. Không cần git pull hoặc xóa các thay đổi chưa commit.
