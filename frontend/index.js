// frontend/index.js

// 1. KHỞI TẠO BẢN ĐỒ LEAFLET
// Cài đặt view mặc định tại Hà Nội
const map = L.map('map').setView([21.0285, 105.8542], 13);

// Thêm lớp bản đồ từ OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

let currentMarker = null;

// 2. LẮNG NGHE SỰ KIỆN CLICK TRÊN BẢN ĐỒ
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lng = e.latlng.lng;

    // Di chuyển hoặc tạo marker mới tại điểm click
    if (currentMarker) {
        currentMarker.setLatLng(e.latlng);
    } else {
        currentMarker = L.marker(e.latlng).addTo(map);
    }

    // Gọi hàm fetch phân tích
    predictCustomLocation(lat, lng);
});

// 3. HÀM GỌI API DỰ ĐOÁN
async function predictCustomLocation(lat, lng) {
    const loadingOverlay = document.getElementById('loading-overlay');
    const statusCard = document.getElementById('status-card');
    
    // Hiển thị loading overlay
    loadingOverlay.classList.remove('hidden');
    // Reset viền màu trong lúc tải
    statusCard.className = 'status-card-base';

    try {
        // Gửi POST request kèm theo tọa độ
        const response = await fetch('/api/predict-location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ lat: lat, lng: lng })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Có lỗi xảy ra từ máy chủ");
        }

        // Cập nhật giao diện khi có kết quả
        updateUI(data);

    } catch (error) {
        console.error("Lỗi:", error);
        alert(`Không thể lấy dự đoán: ${error.message}`);
        
        // Trả UI về trạng thái mặc định nếu lỗi
        document.getElementById('emoji').textContent = "❌";
        document.getElementById('level-text').textContent = "Lỗi kết nối";
    } finally {
        // Ẩn loading overlay khi xong
        loadingOverlay.classList.add('hidden');
    }
}

// 4. HÀM CẬP NHẬT GIAO DIỆN VỚI DỮ LIỆU JSON
function updateUI(data) {
    const level = data.congestion_level;
    const flow = data.flow_predicted;
    const details = data.details;
    const loc = data.location;
    
    // Set emoji
    let emoji = '❓';
    if (level === "Thấp") emoji = "🟢";
    else if (level === "Vừa phải") emoji = "🟡";
    else if (level === "Cao") emoji = "🟠";
    else if (level.includes("Tắc nghẽn nặng")) emoji = "🔴";

    // Cập nhật text chính
    document.getElementById('location-coord').textContent = `Tọa độ: ${loc.lat.toFixed(5)}, ${loc.lng.toFixed(5)}`;
    document.getElementById('emoji').textContent = emoji;
    document.getElementById('level-text').textContent = level.replace('🚨', '').trim();
    document.getElementById('predicted-flow').textContent = flow.toFixed(2);
    
    // Đổi màu Card
    const statusCard = document.getElementById('status-card');
    statusCard.className = 'status-card-base'; 
    const statusClass = 'status-' + level.replace(/ /g, '_').replace('🚨', '').trim();
    statusCard.classList.add(statusClass);

    // Cập nhật thông số chi tiết
    document.getElementById('avg-speed').textContent = `${parseFloat(details.speed).toFixed(1)} km/h`;
    document.getElementById('temperature').textContent = `${details.temp}°C`;
    document.getElementById('weather-status').textContent = details.weather;
}