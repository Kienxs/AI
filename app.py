# app.py (Phiên bản đã tối ưu)
import os
import pandas as pd
import joblib
import holidays
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from utils.traffic_scraper import get_google_maps_speed
from threading import Lock
import requests # Import requests trực tiếp vào đây

# Tạo một ổ khóa toàn cục
scrape_lock = Lock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ [Hệ thống] Đã tải mô hình thành công.")
except Exception as e:
    print(f"❌ [Lỗi] Không thể tải mô hình: {e}")
    model = None

# Đưa hàm lấy thời tiết vào thẳng app.py cho gọn
def get_real_weather(lat, lng):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true&temperature_unit=celsius&timezone=auto"
        res = requests.get(url, timeout=5).json()
        temp = res["current_weather"]["temperature"]
        weather_code = res["current_weather"]["weathercode"]
        rain_flag = 1 if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82] else 0
        return temp, rain_flag
    except Exception as e:
        print(f"Lỗi lấy thời tiết: {e}")
        return 30, 0  

def classify(flow):
    if flow < 400: return "Thấp"
    elif flow < 650: return "Vừa phải"
    elif flow < 900: return "Cao"
    else: return "Tắc nghẽn nặng 🚨"

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/predict-location", methods=["POST"])
def predict_custom_location():
    data = request.json
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({"error": "Thiếu tọa độ lat/lng"}), 400
        
    lat = data['lat']
    lng = data['lng']
    
    try:
        # KHÓA LUỒNG: Bắt buộc Chrome chỉ chạy 1 tiến trình cùng lúc
        with scrape_lock: 
            avg_speed, green_time = get_google_maps_speed(lat, lng)

        # Cào tốc độ tại tọa độ
        avg_speed, green_time = get_google_maps_speed(lat, lng)
        
        # Lấy thời tiết
        temp, rain = get_real_weather(lat, lng)
        
        # Tính toán thời gian
        now = datetime.now()
        vn_holidays = holidays.VN() 
        is_holiday = 1 if (now in vn_holidays or now.weekday() >= 5) else 0
        is_peak_hour = (7 <= now.hour <= 9) or (16 <= now.hour <= 19)
        event_flag = 1 if (avg_speed < 10 and not is_peak_hour) else 0

        features = [
            "avg_speed", "green_time", "rain", "temp", "event_flag",
            "hour_of_day", "day_of_week", "is_holiday", "minute"
        ]
        
        input_row = {
            "avg_speed": avg_speed, "green_time": green_time, "rain": rain, "temp": temp,
            "event_flag": event_flag, "hour_of_day": now.hour, 
            "day_of_week": now.weekday() + 1, "is_holiday": is_holiday, 
            "minute": now.minute
        }
        
        df_input = pd.DataFrame([input_row])
        pred_flow = model.predict(df_input[features])[0]
        level = classify(pred_flow)
        
        return jsonify({
            "status": "success",
            "location": {"lat": lat, "lng": lng},
            "congestion_level": level,
            "flow_predicted": round(float(pred_flow), 2),
            "details": {
                "speed": avg_speed,
                "weather": "Mưa" if rain else "Khô ráo",
                "temp": temp
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)