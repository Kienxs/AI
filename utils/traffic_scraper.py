from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import numpy as np
import time
import io

def detect_map_speed_from_colors(img):
    """
    Nhận dạng màu giao thông từ screenshot Google Maps.
    Trả về tốc độ ước tính (km/h).
    """

    arr = np.array(img)

    # Lấy vùng trung tâm – nơi chứa đường lớn
    h, w, _ = arr.shape
    crop = arr[h//3:2*h//3, w//3:2*w//3]

    # Tính giá trị trung bình màu
    avg = crop.mean(axis=(0, 1))  # [R,G,B]
    r, g, b = avg[:3]

    # Mapping màu → tốc độ
    if g > 150 and r < 120:      # Xanh lá
        return 50
    if r > 200 and g > 160:      # Vàng
        return 30
    if r > 200 and g < 120:      # Cam
        return 15
    if r > 150 and g < 80:       # Đỏ
        return 10

    # Không nhận dạng được → default
    return 30

def get_google_maps_speed(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage") #tránh tràn bộ nhớ
    chrome_options.add_argument("--disable-gpu") #tối ưu hóa việc chụp màn hình
    chrome_options.add_argument("--window-size=1920, 1080")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.get(url)
    time.sleep(5)  # chờ map load

    # Chụp màn hình
    png = driver.get_screenshot_as_png()
    driver.quit()

    img = Image.open(io.BytesIO(png))

    # Dự đoán tốc độ từ màu
    estimated_speed = detect_map_speed_from_colors(img)

    # Green time → bạn đặt cố định hoặc tự mô phỏng
    green_time = 60

    return estimated_speed, green_time

# TEST
if __name__ == "__main__":
    url = "https://www.google.com/maps/@10.8494091,106.7736484,19z/data=!5m1!1e1"
    sp, gr = get_google_maps_speed(url)
    print("Speed:", sp, "km/h.  Green:", gr)
