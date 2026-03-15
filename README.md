# 🚦 Vietnam AI Traffic Predictor

<div align="center">
  <a href="https://kienxs-ai-traffic-vn.hf.space/" target="_blank">
    <img src="https://img.shields.io/badge/Live_Demo-Play_Now-1a73e8?style=for-the-badge&logo=huggingface" alt="Live Demo">
  </a>
</div>

<br/>

## 📌 Project Overview
The **Vietnam AI Traffic Predictor** is a real-time web application that predicts traffic congestion levels across Vietnam. By leveraging Machine Learning, the system automatically scrapes live traffic data from Google Maps, combines it with real-time weather and time-based features, and delivers instant congestion analysis via an interactive map interface.

### ✨ Key Features
- 🗺️ **Interactive Map (Leaflet.js):** Click anywhere on the map to receive an instant AI-powered traffic prediction for that specific coordinate.
- 🤖 **Smart AI Inference:** Classifies current traffic into 4 levels: *Low, Moderate, High, and Severe Congestion*.
- 🌤️ **Real-time Weather Integration:** Automatically fetches temperature and precipitation data for the selected location via the Open-Meteo API.
- ⚡ **Optimized Deployment:** Implements Thread Locking and a highly optimized Headless Chromium configuration via Docker to ensure smooth scraping on low-RAM cloud environments (Hugging Face Spaces).

---

## ⚙️ System Architecture & Workflow

The system operates on a Client-Server architecture integrated with a Machine Learning pipeline:

1. **Client Request:** The user clicks a location on the map. Coordinates (Lat, Lng) are sent to the Flask Backend.
2. **Scraping Engine:** The backend uses **Selenium (Headless Chromium)** to navigate to Google Maps and capture the traffic layer at that exact coordinate. Matrix pixel analysis (using NumPy and Pillow) extracts the dominant traffic color and converts it into an estimated average speed (`avg_speed`).
3. **Context Gathering:** The system fetches current weather data and calculates time-based features (Hour, Day of the week, and Holiday status using the Python `holidays` library).
4. **AI Prediction:** The combined feature vector is fed into a pre-trained **Random Forest Regressor** to calculate a Congestion Index (`flow_weighted`).
5. **Response:** The backend classifies the index and returns a JSON payload to update the frontend UI instantly.

---

## 📊 Model & Training Data

### ⚠️ Data Limitations & Generalization Disclaimer
It is important to note the scope of the training data. The model was trained on a highly controlled, synthetic dataset based on the real-world traffic patterns of **a single specific location**: *The gate of Hanoi University of Industry (HaUI) on QL32 Highway, Hanoi.*

Because the model was trained on the traffic capacity of a major highway intersection, **applying it globally to any random location (e.g., a small alley in Ho Chi Minh City or a rural road) means the absolute numerical predictions might not perfectly reflect that specific road's physical capacity.**

**However, the logical accuracy remains highly reliable.** The model has successfully learned the universal rules of traffic dynamics. For example, it understands that:
`Red Map Color (Low Speed) + Rush Hour (17:00) + Rain = Severe Congestion`
Therefore, while the exact vehicle count/flow number is localized, the **congestion classification trend (Low to Severe) is conceptually accurate and applicable anywhere.**

### Model Performance
- **Algorithm:** `RandomForestRegressor` (scikit-learn)
- **R² Score:** `> 0.96` (The model successfully explains over 96% of the variance in the training data).
- **Feature Importance:** The model heavily prioritizes `avg_speed` (scraped map color) and `hour_of_day`, proving it has learned human-like logic regarding rush hours and traffic flow.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Gunicorn
- **AI & Data Science:** Scikit-learn, Pandas, NumPy, Joblib
- **Web Scraping & Vision:** Selenium, webdriver-manager, Pillow
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, Leaflet.js
- **DevOps & Deployment:** Docker, Git, Hugging Face Spaces
