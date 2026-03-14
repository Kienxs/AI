# Sử dụng Python bản gọn nhẹ nhất
FROM python:3.11-slim

# Cài đặt các công cụ hệ thống và Chromium (phiên bản Chrome cho Linux) siêu nhẹ
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code vào Docker
COPY . .

# Chỉ định cổng chạy
EXPOSE 5000

# Chạy app bằng Gunicorn (chỉ dùng 1 worker để tiết kiệm RAM)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "app:app"]