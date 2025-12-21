// frontend/index.js

// Hàm cập nhật giao diện người dùng với dữ liệu JSON nhận được
function updateUI(data) {
    if (!data || data.length === 0) {
        // Xử lý trường hợp không có dữ liệu
        document.getElementById('level-text').textContent = 'Không có dữ liệu';
        document.getElementById('emoji').textContent = '⚠️';
        document.getElementById('timestamp').textContent = 'Lỗi hoặc chưa có dự đoán.';
        return;
    }

    // Lấy bản ghi mới nhất (API trả về mảng, lấy phần tử đầu tiên)
    const row = data[0]; 

    // Chuẩn hóa và thêm emoji (do API Python chưa tự động thêm emoji)
    const level = row.congestion_level;
    const flow = row.flow_weighted_pred;
    
    let emoji = '❓';
    if (level === "Thấp") emoji = "🟢";
    else if (level === "Vừa phải") emoji = "🟡";
    else if (level === "Cao") emoji = "🟠";
    else if (level.includes("Tắc nghẽn nặng")) emoji = "🔴";

    // 1. Cập nhật trạng thái chính
    // Sử dụng date string từ row.timestamp
    document.getElementById('timestamp').textContent = `Thời gian: ${row.timestamp}`; 
    document.getElementById('emoji').textContent = emoji;
    document.getElementById('level-text').textContent = level.replace('🚨', '').trim();
    document.getElementById('predicted-flow').textContent = parseFloat(flow).toFixed(2);
    
    // 2. Cập nhật màu sắc động
    const statusCard = document.getElementById('status-card');
    statusCard.className = 'status-card-base'; // Khởi tạo lại lớp cơ sở
    const statusClass = 'status-' + level.replace(/ /g, '_').replace('🚨', '').trim();
    statusCard.classList.add(statusClass);

    // 3. Cập nhật dữ liệu đầu vào
    document.getElementById('avg-speed').textContent = `${parseFloat(row.avg_speed).toFixed(1)} km/h`;
    document.getElementById('green-time').textContent = `${row.green_time} giây`;
    document.getElementById('temperature').textContent = `${row.temp}°C`;
    document.getElementById('rain-flag').textContent = row.rain === 1 ? "Có Mưa 🌧️" : "Khô ráo ☀️";
    document.getElementById('moto-count').textContent = row.motorbike_count;
    document.getElementById('car-count').textContent = row.car_count;

    const eventElem = document.getElementById('event-flag');
    const holidayElem = document.getElementById('is-holiday');

    // Hiển thị trạng thái Sự kiện/Sự cố
    if (row.event_flag === 1) {
        eventElem.innerHTML = '<span style="color: #e74c3c; font-weight: bold;">Có sự cố/Sự kiện ⚠️</span>';
    } else {
        eventElem.textContent = "Bình thường ✅";
    }

    // Hiển thị trạng thái Ngày lễ
    if (row.is_holiday === 1) {
        holidayElem.innerHTML = '<span style="color: #f39c12; font-weight: bold;">Ngày Lễ/Nghỉ 🎉</span>';
    } else {
        holidayElem.textContent = "Ngày thường 💼";
    }
}


// Hàm gọi API để lấy dữ liệu mới nhất
async function fetchData() {
    const refreshBtn = document.getElementById('refresh-btn');
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Đang Cập nhật...';

    try {
        // API này sẽ gọi real_time_predict.py và trả về kết quả dự đoán mới nhất
        const predictionResponse = await fetch('/api/run-prediction'); 
        
        if (!predictionResponse.ok) {
            const errorData = await predictionResponse.json();
            throw new Error(`Lỗi Server: ${errorData.error}`);
        }
        
        // Sau khi chạy xong, gọi lại /api/realtime để lấy dữ liệu đã được format
        const realtimeResponse = await fetch('/api/realtime');
        const data = await realtimeResponse.json();
        
        // Kiểm tra lỗi từ script Python/Server
        if (Array.isArray(data) && data[0]?.error) {
            alert('Lỗi từ Server: ' + data[0].error);
        } else {
            updateUI(data);
        }

    } catch (error) {
        console.error("Lỗi khi lấy dữ liệu:", error);
        alert(`Không thể cập nhật: ${error.message}`);
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.textContent = 'Cập nhật Ngay';
    }
}

// Gọi lần đầu khi tải trang
fetchData();

// Thêm sự kiện cho nút Cập nhật Ngay
document.getElementById('refresh-btn').addEventListener('click', fetchData);