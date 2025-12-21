import os
import json
import pandas as pd
import joblib
import threading
import holidays
import time
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request

# Import các hàm từ các module bạn đã viết
from utils.traffic_scraper import get_google_maps_speed
from utils.traffic_estimate import estimate_traffic_counts
from predict.real_time_predict import get_real_weather, classify

# ===========================
# CONFIG & PATHS
# ===========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "traffic_data.csv")
PREDICTION_CSV_PATH = os.path.join(BASE_DIR, "real_time_prediction.csv")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# ===========================
# 1. LOAD MODEL (GLOBAL)
# ===========================
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ [Hệ thống] Đã tải mô hình thành công.")
except Exception as e:
    print(f"❌ [Lỗi] Không thể tải mô hình: {e}")
    model = None

# Biến toàn cục để lưu kết quả mới nhất (Cache)
latest_prediction = {}

# ===========================
# 2. HÀM DỰ ĐOÁN CỐT LÕI (CORE LOGIC)
# ===========================
def process_traffic_prediction():
    global latest_prediction
    try:
        # 1. Cào dữ liệu Google Maps (HaUI)
        url = "http://googleusercontent.com/maps.google.com/8"
        avg_speed, green_time = get_google_maps_speed(url)
        
        # 2. Lấy thời tiết & Ước lượng xe
        temp, rain = get_real_weather()
        moto, car, bus = estimate_traffic_counts(avg_speed)
        
        now = datetime.now()
        
        vn_holidays = holidays.VN() 
        is_holiday = 1 if (now in vn_holidays or now.weekday() >= 5) else 0
        
        # Logic Sự cố (event_flag): 
        # Thực tế rất khó cào sự cố real-time, nên ta dùng logic dựa trên tốc độ:
        # Nếu tốc độ cực thấp (< 10km/h) mà không phải giờ cao điểm -> Có thể có sự cố
        is_peak_hour = (7 <= now.hour <= 9) or (16 <= now.hour <= 19)
        event_flag = 1 if (avg_speed < 10 and not is_peak_hour) else 0

        # 3. Chuẩn bị dữ liệu cho Model
        features = [
            "avg_speed", "green_time", "rain", "temp", "event_flag",
            "hour_of_day", "day_of_week", "is_holiday",
            "motorbike_count", "car_count", "bus_count", "minute"
        ]
        
        input_row = {
            "avg_speed": avg_speed, "green_time": green_time, "rain": rain, "temp": temp,
            "event_flag": event_flag, 
            "hour_of_day": now.hour, 
            "day_of_week": now.weekday() + 1,
            "is_holiday": is_holiday, 
            "motorbike_count": moto, "car_count": car, "bus_count": bus,
            "minute": now.minute
        }
        
        df_input = pd.DataFrame([input_row])
        
        # 4. Dự đoán
        pred_flow = model.predict(df_input[features])[0]
        level = classify(pred_flow)
        
        # 5. Lưu kết quả vào biến Global để Frontend lấy
        result = {
            "timestamp": now.strftime('%Y-%m-%d %H:%M:%S'),
            "flow_weighted_pred": round(float(pred_flow), 2),
            "congestion_level": level,
            "avg_speed": avg_speed,
            "green_time": green_time, 
            "temp": temp,          
            "rain": "Mưa" if rain == 1 else "Khô ráo", 
            "motorbike_count": moto, 
            "car_count": car,      
            "bus_count": bus,
            "event_flag": event_flag, 
            "is_holiday": is_holiday,    
        }
        latest_prediction = result
        
        # 6. Ghi vào file CSV
        df_input["timestamp"] = now
        df_input["flow_weighted_pred"] = pred_flow
        df_input["congestion_level"] = level
        
        header = not os.path.exists(PREDICTION_CSV_PATH)
        df_input.to_csv(PREDICTION_CSV_PATH, mode='a', index=False, header=header)
        
        return result
    except Exception as e:
        print(f"❌ [Lỗi Dự Đoán]: {e}")
        return None

# ===========================
# 3. BACKGROUND THREAD (LUỒNG CHẠY NGẦM)
# ===========================
def background_worker():
    while True:
        process_traffic_prediction()
        # Nghỉ 5 phút 
        time.sleep(300)

# Khởi chạy luồng ngầm ngay khi app start
threading.Thread(target=background_worker, daemon=True).start()

# ===========================
# 4. API ROUTES
# ===========================

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/run-prediction")
def trigger_prediction():
    res = process_traffic_prediction()
    if res:
        return jsonify({"message": "Cập nhật thành công", "data": res})
    return jsonify({"error": "Không thể lấy dữ liệu từ Google Maps"}), 500

@app.route("/api/realtime")
def get_latest():
    if not latest_prediction:
        return jsonify({"message": "Đang khởi tạo dữ liệu..."}), 202
    return jsonify([latest_prediction])

@app.route("/api/data")
def get_history():
    if not os.path.exists(DATA_PATH):
        return jsonify({"error": "Data file not found"}), 404
    df = pd.read_csv(DATA_PATH)
    return df.to_json(orient="records")

# ===========================
# START SERVER
# ===========================
if __name__ == "__main__":
    # Tắt debug=True khi dùng Threading để tránh bị khởi chạy luồng 2 lần
    app.run(host="0.0.0.0", port=5000, debug=False)