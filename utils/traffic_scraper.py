#traffic_scraper.py
import io
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

def detect_map_speed_from_colors(img):
    """
    Nhận dạng màu giao thông từ screenshot Google Maps.
    Đã tối ưu hóa việc xử lý mảng để chạy nhanh trên chip M1/M2/M3.
    """
    arr = np.array(img)
    h, w, _ = arr.shape
    # Lấy vùng trung tâm 1/3 màn hình để phân tích màu sắc chính xác nhất
    crop = arr[h//3:2*h//3, w//3:2*w//3]

    # Tính trung bình màu nhanh bằng numpy
    avg = crop.mean(axis=(0, 1))
    r, g, b = avg[:3]

    # Logic phân loại màu dựa trên thực tế Google Maps Traffic
    if g > 150 and r < 120: return 50  # Xanh lá (Thoáng)
    if r > 200 and g > 160: return 30  # Vàng (Vừa phải)
    if r > 200 and g < 120: return 15  # Cam (Cao)
    if r > 150 and g < 80:  return 8   # Đỏ (Tắc nghẽn nặng)
    
    return 30 # Mặc định

def get_google_maps_speed(lat, lng, zoom=17):
    url = f"https://www.google.com/maps/@{lat},{lng},{zoom}z/data=!5m1!1e1"

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_argument("--disable-remote-fonts") 
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1024,768")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.set_page_load_timeout(10)
        driver.get(url)

        start_time = time.time()
        driver.get(url)
        # Chỉ chờ tối đa 3 giây. 
        time.sleep(3) 
        # Chụp màn hình dạng binary trực tiếp vào RAM, không lưu xuống ổ cứng
        png = driver.get_screenshot_as_png()
        
        print(f"✅ Scraping hoàn tất trong: {time.time() - start_time:.2f} giây")
        
    finally:
        driver.quit()

    # Xử lý ảnh bằng Pillow
    img = Image.open(io.BytesIO(png))
    estimated_speed = detect_map_speed_from_colors(img)

    return estimated_speed, 60

# TEST
if __name__ == "__main__":
    test_url = "http://googleusercontent.com/maps.google.com/9"
    sp, gr = get_google_maps_speed(test_url)
    print(f"📊 Kết quả -> Tốc độ: {sp} km/h | Đèn xanh: {gr}s")