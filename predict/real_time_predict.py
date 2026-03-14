# predict/real_time_predict.py
from datetime import datetime
import pandas as pd
import joblib
import requests
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.traffic_scraper import get_google_maps_speed

def get_real_weather(lat, lng):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true&temperature_unit=celsius&timezone=auto"
        res = requests.get(url, timeout=5).json()
        
        temp = res["current_weather"]["temperature"]
        weather_code = res["current_weather"]["weathercode"]
        
        # Các mã Open-Meteo thể hiện có mưa
        rain_flag = 1 if weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82] else 0
        
        return temp, rain_flag
    
    except Exception as e:
        return 30, 0  


# ==== Load model ====
MODEL_PATH = "models/model.pkl"
model = joblib.load(MODEL_PATH)

url = "https://www.google.com/maps/@21.0537,105.7351,17z/data=!5m1!1e1"
avg_speed, green_time = get_google_maps_speed(url)
temp, rain = get_real_weather()
now = datetime.now()

new_data = {
    "timestamp": [now],
    "avg_speed": [avg_speed],
    "green_time": [green_time],
    "rain": [rain],
    "temp": [temp],
    "event_flag": [0],
    "hour_of_day": [now.hour],
    "day_of_week": [now.weekday() + 1],
    "is_holiday": [0],
    "minute": [now.minute]
}

new_df = pd.DataFrame(new_data)

# ==== Dự đoán ====
features = [
    "avg_speed", "green_time", "rain", "temp", "event_flag",
    "hour_of_day", "day_of_week", "is_holiday", "minute"
]
new_df["flow_weighted_pred"] = model.predict(new_df[features])

# ==== Phân loại tắc nghẽn ====
def classify(flow):
    if flow < 400: return "Thấp"
    elif flow < 650: return "Vừa phải"
    elif flow < 900: return "Cao"
    else: return "Tắc nghẽn nặng 🚨"

new_df["congestion_level"] = new_df["flow_weighted_pred"].apply(classify)

# ==== Emoji hiển thị ====
emojis = {
    "Thấp": "🟢",
    "Vừa phải": "🟡",
    "Cao": "🟠",
    "Tắc nghẽn nặng 🚨": "🔴"
}

# ==== In kết quả  ====
print("\n--- Dự đoán giao thông nút giao hiện tại ---\n")
for _, row in new_df.iterrows():
    icon = emojis.get(row["congestion_level"], "🚧")
    print(f"{icon}  ⏱ {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}  ➜  "
          f"{row['congestion_level']} (Flow dự đoán: {row['flow_weighted_pred']:.2f})")

csv_path = "real_time_prediction.csv"

# Nếu file đã tồn tại → append và KHÔNG ghi header
if os.path.exists(csv_path):
    new_df.to_csv(csv_path, mode='a', header=False, index=False)
else:
    # Nếu file chưa tồn tại → ghi đầy đủ (có header)
    new_df.to_csv(csv_path, mode='w', header=True, index=False)

print("\n💾 Kết quả đã được lưu vào file: real_time_prediction.csv")


# python -m predict.real_time_predict
