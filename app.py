from flask import Flask, send_from_directory, jsonify, request
import pandas as pd
import joblib
import os
from datetime import datetime
import subprocess # Cần cho việc chạy script Python khác
import json

# ===========================
# CONFIG
# ===========================
FRONTEND_DIR = "frontend"
DATA_PATH = "data/traffic_data.csv"
MODEL_PATH = "models/model.pkl"
PREDICT_SCRIPT_PATH = "predict/real_time_predict.py"
PREDICTION_CSV_PATH = "real_time_prediction.csv"

app = Flask(__name__, static_folder=FRONTEND_DIR, template_folder=FRONTEND_DIR)

# Tải model (Bỏ qua tạm thời nếu chưa có model.pkl)
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅ Đã tải mô hình từ: {MODEL_PATH}")
except Exception as e:
    print(f"⚠️ LỖI: Không thể tải mô hình ({MODEL_PATH}). Vui lòng huấn luyện mô hình trước. Lỗi: {e}")
    model = None


# ==========================================
# 1. SERVE FRONTEND & STATIC FILES
# ==========================================

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)


# ==========================================
# 2. API — KÍCH HOẠT DỰ ĐOÁN THỜI GIAN THỰC
# ==========================================

# Đoạn code trong file app.py
# ...

# ==========================================
# 2. API — KÍCH HOẠT DỰ ĐOÁN THỜI GIAN THỰC
# ==========================================

@app.route("/api/run-prediction")
def run_prediction():
    try:
        print("[+] Kích hoạt dự đoán...")

        process = subprocess.Popen(
            ["python", PREDICT_SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False  # ← NHẬN RAW BYTES, KHÔNG ÉP UTF-8
        )

        stdout, stderr = process.communicate()

        # decode an toàn
        stdout = stdout.decode("utf-8", errors="ignore") if stdout else ""
        stderr = stderr.decode("utf-8", errors="ignore") if stderr else ""

        print("STDOUT:", stdout)
        print("STDERR:", stderr)

        if process.returncode != 0:
            return jsonify({
                "error": f"Lỗi khi chạy script dự đoán",
                "stderr": stderr
            }), 500

        return jsonify({"message": "Chạy dự đoán thành công!", "stdout": stdout})

    except Exception as e:
        print("❌ Lỗi:", e)
        return jsonify({"error": f"Lỗi Server: {str(e)}"}), 500

# ==========================================
# 3. API — LẤY FILE real_time_prediction.csv
# ==========================================

@app.route("/api/realtime")
def get_real_time():
    if not os.path.exists(PREDICTION_CSV_PATH):
        # API này có thể được gọi trước khi chạy dự đoán lần đầu
        return jsonify([{"error": "real_time_prediction.csv not found"}]), 404

    df = pd.read_csv(PREDICTION_CSV_PATH)
    
    # Chỉ lấy bản ghi gần nhất và chuyển thành danh sách các đối tượng JSON
    # 'records' trả về một danh sách các dictionary, dễ xử lý trong JS
    latest = json.loads(df.tail(1).to_json(orient="records"))
    return jsonify(latest)


# ==========================================
# 4. API — API KHÁC (giữ lại theo code cũ của bạn)
# ==========================================

@app.route("/api/data")
def get_data():
    if not os.path.exists(DATA_PATH):
        return jsonify({"error": "traffic_data.csv not found"}), 404
    df = pd.read_csv(DATA_PATH)
    return df.to_json(orient="records")

@app.route("/api/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model chưa được tải thành công"}), 500
        
    try:
        data = request.json
        df = pd.DataFrame([data])

        features = [
            "avg_speed", "green_time", "rain", "temp", "event_flag",
            "hour_of_day", "day_of_week", "is_holiday",
            "motorbike_count", "car_count", "bus_count", "minute"
        ]

        pred = model.predict(df[features])[0]

        return jsonify({
            "prediction": round(float(pred), 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)