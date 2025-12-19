# RF.py
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import joblib

# ==========================================
# 1. ĐƯỜNG DẪN
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/traffic_data.csv")  # file CSV train
MODEL_PATH = "model.pkl"                 # file model lưu vào thư mục hiện tại

# ==========================================
# 2. LOAD DATA
# ==========================================
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Không tìm thấy file train: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True)
df["minute"] = df["timestamp"].dt.minute

target = "flow_weighted"
features = [
    "avg_speed", "green_time", "rain", "temp", "event_flag",
    "hour_of_day", "day_of_week", "is_holiday",
    "motorbike_count", "car_count", "bus_count", "minute"
]

X = df[features]
y = df[target]

# ==========================================
# 3. KIỂM TRA FILE MODEL
# ==========================================
train_new = False
if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print(f"\n✅ Đã load model từ {MODEL_PATH}")
    except EOFError:
        print(f"\n⚠ File {MODEL_PATH} bị hỏng. Sẽ train lại model.")
        train_new = True
else:
    print(f"\n⚠ Không tìm thấy file {MODEL_PATH}. Sẽ train model mới.")
    train_new = True

# ==========================================
# 4. TRAIN MODEL
# ==========================================
if train_new:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
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

    # Đánh giá
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print("\n==== KẾT QUẢ MÔ HÌNH ====")
    print(f"MAE: {mae:.4f}")
    print(f"R²: {r2:.6f}")

    # Lưu model
    joblib.dump(model, MODEL_PATH)
    print(f"\n💾 Model đã lưu thành công: {MODEL_PATH}")
