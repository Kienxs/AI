# 🚦 Vietnam AI Traffic Predictor

<div align="center">
  <a href="https://kienxs-ai-traffic-vn.hf.space/" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-Play_Now-1a73e8?style=for-the-badge&logo=huggingface" alt="Live Demo">
  </a>
</div>

## 📌 Giới thiệu dự án
Đây là hệ thống dự đoán mức độ ùn tắc giao thông tại Việt Nam theo thời gian thực. Bằng cách sử dụng Machine Learning, hệ thống tự động cào dữ liệu từ bản đồ, kết hợp với các yếu tố thời gian và thời tiết để đưa ra các phân tích và dự báo chính xác ngay trên giao diện Web tương tác.

**Các tính năng chính:**
- 🗺️ **Bản đồ tương tác (Leaflet.js):** Nhấp vào bất kỳ điểm nào trên bản đồ để nhận dự đoán.
- 🤖 **AI Dự đoán thông minh:** Phân loại mức độ ùn tắc (Thấp, Vừa phải, Cao, Tắc nghẽn nặng) với độ chính xác cao.
- 🌤️ **Tích hợp thời tiết:** Tự động lấy dữ liệu nhiệt độ và tình trạng mưa tại vị trí được chọn.
- ⚡ **Tối ưu hóa máy chủ:** Xử lý luồng (Lock Threading) và tối ưu Chrome Headless trên Docker để chạy mượt mà trên môi trường RAM thấp.

---

## ⚙️ Luồng hoạt động của hệ thống (System Architecture)

Hệ thống hoạt động theo mô hình Client-Server kết hợp luồng xử lý AI:

1. **Client (Frontend):** Người dùng nhấp vào một điểm trên bản đồ Leaflet. Tọa độ (Lat, Lng) được gửi đến Backend thông qua API `/api/predict-location`.
2. **Scraping Engine:** Backend sử dụng **Selenium (Headless Chromium)** để truy cập Google Maps với layer Giao thông tại tọa độ đó. Phân tích ma trận điểm ảnh (Pixels) để trích xuất màu giao thông và quy đổi thành Vận tốc trung bình (`avg_speed`).
3. **Weather API:** Gọi Open-Meteo API để lấy thông tin nhiệt độ và lượng mưa.
4. **Data Preprocessing:** Tổng hợp dữ liệu tốc độ, thời tiết, kết hợp với thời gian thực (Giờ, Ngày trong tuần, Ngày lễ sử dụng thư viện `holidays`).
5. **AI Inference:** Đưa vector đặc trưng vào mô hình **Random Forest Regressor** để tính toán "Chỉ số ách tắc" (`flow_weighted`).
6. **Response:** Backend phân loại mức độ và trả kết quả (JSON) về cho giao diện hiển thị ngay lập tức.

---

## 📊 Mô hình & Dữ liệu Huấn luyện (Training Data)

### 1. Dữ liệu (Dataset)
Do dữ liệu lịch sử giao thông chi tiết không có sẵn, mình đã xây dựng một Script để tạo dữ liệu giả lập (Synthetic Data) có kiểm soát chặt chẽ dựa trên **đặc thù giao thông thực tế tại cổng trường Đại học Công nghiệp Hà Nội (HaUI - QL32)** trong 3 tháng (Tháng 10 - 12/2025).

**Các đặc trưng (Features) đưa vào huấn luyện:**
- `avg_speed`: Tốc độ trung bình (Quy đổi từ màu của bản đồ).
- `hour_of_day`, `minute`, `day_of_week`: Yếu tố thời gian.
- `is_holiday`: Gắn nhãn ngày lễ/cuối tuần (Sinh viên nghỉ học -> Đường vắng hơn).
- `rain`, `temp`: Thời tiết.
- `event_flag`: Sự cố ngẫu nhiên.

### 2. Huấn luyện Mô hình
- **Thuật toán:** `RandomForestRegressor` từ thư viện `scikit-learn`.
- **Kết quả đánh giá:** - **R² Score:** > 0.96 (Mô hình giải thích được >96% sự biến thiên của giao thông thực tế).
  - **Feature Importances:** Tốc độ (avg_speed) và Giờ cao điểm (hour_of_day) được mô hình đánh giá là 2 yếu tố quyết định lớn nhất, hoàn toàn khớp với logic của con người.

---

## 🛠️ Công nghệ sử dụng (Tech Stack)
- **Backend:** Python, Flask, Gunicorn
- **AI & Data:** Scikit-learn, Pandas, NumPy, Joblib
- **Scraping:** Selenium, webdriver-manager, Pillow (Image Processing)
- **Frontend:** HTML5, CSS3, Vanilla JS, Leaflet.js
- **DevOps & Deployment:** Docker, Hugging Face Spaces



# 4. Khởi chạy Server
python app.py
