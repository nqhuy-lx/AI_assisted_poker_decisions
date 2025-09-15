## ▶️ Hướng dẫn sử dụng chi tiết

Để sử dụng công cụ này đúng cách, bạn cần làm theo các bước sau.  
⚠️ Lưu ý: Chương trình hiện tại **chỉ hỗ trợ hệ điều hành Windows**.


### 1. Mở game Poker trên web
1. Mở trình duyệt (khuyến nghị: **Google Chrome hoặc Microsoft Edge**).  
2. Truy cập trang: [https://www.247freepoker.com/](https://www.247freepoker.com/).  
3. Trên màn hình chính của website:
   - Nhấn nút **Play** để bắt đầu.  
   - Nhấn **New Game** để khởi động một ván bài mới.  
   - Chọn chế độ chơi bạn muốn (ví dụ: easy).  
   - Và để màn hình web như sau
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/37a60e06-0d79-4bb1-b409-14df694dd332" />
  
📌 Lưu ý:  
- Đảm bảo cửa sổ game được mở toàn màn hình hoặc ít nhất không bị che khuất.  
- Zoom trình duyệt = **100%** và Scale Windows = **100%** để công cụ nhận diện chính xác.  


### 2. Chuẩn bị màn hình chơi

- Sau khi ván bài bắt đầu, hãy để màn hình game hiển thị đầy đủ (bàn poker, lá bài, nút Call/Check, Raise, Fold).  
- **Không thu nhỏ (minimize)** hoặc chuyển sang tab khác — vì công cụ cần chụp ảnh màn hình để phân tích.
  
### 3. Cài đặt Python và pip (nếu chưa có)

1. Tải Python bản mới nhất (khuyến nghị **Python 3.10+**) tại:  
   :point_right: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)  
   Khi cài đặt, nhớ tick chọn **"Add Python to PATH"**.  

2. Kiểm tra cài đặt Python và pip:
     powershell
     python --version
     pip --version
   
3. Trường hợp đã có sẵn Visual Studio Code
    Mở thư mục chứa source code bằng VS Code
    Mở Terminal trong VS Code (Menu → Terminal → New Terminal).
    Cài thêm các thư viện cần thiết:
    pip install opencv-python
    pip install numpy
    pip install pyautogui
   
4. Trường hợp dùng PyCharm hoặc IntelliJ IDEA

  Mở project trong PyCharm/IntelliJ.
  Vào menu: File → Settings → Project: <tên project> → Python Interpreter.
  Tại đây, bạn có thể:
  Kiểm tra Python Interpreter đang dùng (nên chọn Python 3.x).
  Nhấn + để cài đặt thêm thư viện.
  Cài 3 thư viện cần thiết:
  opencv-python  
  numpy  
  pyautogui
  Sau khi cài, nhấn Apply → OK để lưu cấu hình.
  📌 Nếu muốn pip nhanh bằng terminal trong PyCharm/IntelliJ:
  Mở Terminal ở IDE, gõ lệnh:  
  pip install opencv-python numpy pyautogui
      
