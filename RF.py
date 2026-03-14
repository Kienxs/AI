# RF.py

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# ==========================================
# 1. ĐƯỜNG DẪN & CẤU TRÚC THƯ MỤC
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Đảm bảo đường dẫn tìm đến file data bạn đã lưu
DATA_PATH = os.path.join(BASE_DIR, "data", "traffic_data.csv") 

# Tạo thư mục models nếu chưa có 
MODEL_DIR = os.path.join(BASE_DIR, "models")
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
    print(f"📁 Đã tạo thư mục mới: {MODEL_DIR}")

MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

# ==========================================
# 2. TẢI VÀ TIỀN XỬ LÝ DỮ LIỆU
# ==========================================
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ Không tìm thấy file dữ liệu tại: {DATA_PATH}. "
                            "Hãy đảm bảo bạn đã lưu tệp CSV vào thư mục data/")

print(f"⏳ Đang tải dữ liệu từ {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

# Chuyển đổi timestamp và trích xuất đặc trưng
df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True)
df["minute"] = df["timestamp"].dt.minute


target = "flow_weighted"
features = [
    "avg_speed", "green_time", "rain", "temp", "event_flag",
    "hour_of_day", "day_of_week", "is_holiday", "minute"
]

X = df[features]
y = df[target]

# ==========================================
# 3. HUẤN LUYỆN MÔ HÌNH (RANDOM FOREST)
# ==========================================
print("🚀 Đang huấn luyện mô hình Random Forest...")

# Chia dữ liệu train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Cấu hình Model theo thông số bạn đã chọn
model = RandomForestRegressor(
    n_estimators=150,
    max_depth=8,     
    min_samples_split=10,
    min_samples_leaf=5,
    max_features="sqrt",
    bootstrap=True,
    max_samples=0.8,
    random_state=42
)

model.fit(X_train, y_train)

# ==========================================
# 4. ĐÁNH GIÁ & LƯU MÔ HÌNH
# ==========================================
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n" + "="*30)
print("📊 KẾT QUẢ MÔ HÌNH")
print(f"   - MAE: {mae:.4f}")
print(f"   - R² Score: {r2:.6f}")
print("="*30)

# Lưu model vào thư mục models/
joblib.dump(model, MODEL_PATH)
print(f"\n✅ Đã lưu model thành công tại: {MODEL_PATH}")

# In ra các đặc trưng quan trọng nhất (Feature Importance)
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\n🔝 Các yếu tố ảnh hưởng lớn nhất đến lưu lượng:")
print(importances.head(5))