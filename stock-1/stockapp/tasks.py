import atexit
import re
import threading
from datetime import datetime, timedelta
from pyngrok import ngrok

from stock import settings
def call_api():
    """Hàm thực tế gọi API"""
    print("Gọi API lúc:", datetime.now())
    from stockapp.features.tasks_with_cassandra import insert_stock_info
    insert_stock_info()
    schedule_next()  # Lên lịch cho lần tiếp theo

def schedule_next():
    """Lên lịch gọi API tiếp theo theo bước 15 phút từ 9:15 → 16:00"""
    now = datetime.now()
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday

    # Nếu thứ 7 hoặc CN → không lên lịch
    if weekday >= 5:
        print("Hôm nay là cuối tuần, không lên lịch.")
        return

    # Xác định mốc giờ tiếp theo
    hour = now.hour
    minute = now.minute

    # Bước các phút: 15,30,45,0
    minutes_step = [15,45]

    # Tìm phút tiếp theo
    next_minute = None
    for m in minutes_step:
        if m > minute:
            next_minute = m
            break

    next_hour = hour
    if next_minute is None:
        # sang giờ tiếp theo
        next_minute = minutes_step[0]
        next_hour += 1

    # Nếu đã quá 16h → dừng
    if next_hour >= 17:
        print("Đã quá 16h, kết thúc lịch hôm nay.")
        return

    # Tạo datetime cho lần gọi tiếp theo
    target = now.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)
    delay = (target - now).total_seconds()

    print(f"Lên lịch gọi API lúc {target} (delay {delay:.0f}s)")
    t = threading.Timer(delay, call_api)
    t.daemon = True
    t.start()

ngrok_url=None
ngrok_start=False
lock = threading.Lock()  # Tạo một khóa để đồng bộ hóa
payment_result=0

def start_ngrok():
    global ngrok_url, ngrok_start

    with lock:  # Đảm bảo chỉ một luồng chạy đoạn mã bên trong
        if not ngrok_start:
            try:
                ngrok.set_auth_token(settings.AUTH_TOKEN)
                tunnel = ngrok.connect(8000)
                ngrok_url = tunnel.public_url 
                ngrok_start = True
                print('NGrok', ngrok_url)
                ngrok_host = re.sub(r"^https?://", "", ngrok_url).strip("/")
                settings.ALLOWED_HOSTS.append(ngrok_host)
                atexit.register(ngrok.kill)
            except Exception as e:
                print("Failed to start NGrok:", e)
                raise
    return ngrok_url