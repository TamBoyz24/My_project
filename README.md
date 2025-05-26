# Website hàng onlie
Đây là một website thương mại điện tử đơn giản được xây dựng bằng **Django**, hỗ trợ các chức năng cơ bản như hiển thị sản phẩm, đăng nhập/đăng ký, giỏ hàng và quản lý đơn hàng.
## Tính năg
- Đăng ký / Đăng nhập người dùng
- Danh sách sản phẩm (quần áo)
- Thêm vào giỏ hàng & thanh toán
- Lịch sử đặt hàng và xem hóa đơn
- Quản lý sản phẩm qua trang admin (Django Admin)
##Công nghệ sử dụng
- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Bootstrap
- **Cơ sở dữ liệu**: SQLite
- **Công cụ**: Git, GitHub
## 📁 Cấu Trúc Thư Mục
clothing_store/
│
├── store/
│ ├── models.py
│ ├── views.py
│ ├── templates/
│ ├── static/
│
├── clothing_store/
│ ├── settings.py
│ ├── urls.py
│
└── manage.py
##
## 💡 Cách Chạy Dự Án Trên Máy

1. Clone repo:
git clone https://github.com/TamBoyz24/My_project.git
cd My_project



2. Tạo và kích hoạt môi trường ảo:
python -m venv venv
venv\Scripts\activate


3. Cài đặt các thư viện cần thiết (nếu có file `requirements.txt`):
pip install -r requirements.txt


4. Chạy server:
python manage.py runserver



Sau đó mở trình duyệt và truy cập:  
`http://127.0.0.1:8000/`




⭐ Cảm ơn Thầy và anh Vũ đã ghé thăm project này!
