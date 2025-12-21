import random

def estimate_traffic_counts(avg_speed):
    """
    Ước tính số lượng xe dựa theo tốc độ giao thông.
    Chia theo 4 mức: Xanh, Vàng, Đỏ, Đỏ đậm giống Google Maps.
    Mỗi mức có khoảng dao động tự nhiên.
    """

    speed = max(0.1, min(avg_speed, 60))

    # ============================
    # 1) MỨC XANH – RẤT THOÁNG
    # ============================
    if speed >= 45:
        motorbike = random.randint(150, 500)
        car       = random.randint(42, 94)
        bus       = random.randint(8, 22)

    # ============================
    # 2) MỨC VÀNG – TRUNG BÌNH
    # ============================
    elif speed >= 25:
        motorbike = random.randint(400, 625)
        car       = random.randint(74, 177)
        bus       = random.randint(12, 28)

    # ============================
    # 3) MỨC ĐỎ – ÙN Ứ
    # ============================
    elif speed >= 10:
        motorbike = random.randint(525, 775)
        car       = random.randint(127, 258)
        bus       = random.randint(24, 44)

    # ============================
    # 4) MỨC ĐỎ ĐẬM – KẸT XE NẶNG
    # ============================
    else:
        motorbike = random.randint(625, 820)
        car       = random.randint(280, 678)
        bus       = random.randint(28, 51)

    return motorbike, car, bus
