import psutil
import time

def monitor_and_log(interval_sec=1, log_file="system_monitor.log"):
    time_ = 0
    try:
        with open(log_file, 'w') as f:
            while True:
                time_ = time_ + 1
                # Lấy thông tin về RAM
                ram = psutil.virtual_memory()
                ram_info = f"RAM - Total: {ram.total} bytes, Used: {ram.used} bytes, Available: {ram.available} bytes\n"

                # Lấy thông tin về CPU
                cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
                cpu_info = "CPU - Usage percentages: " + ", ".join([f"{i+1}: {percent}%" for i, percent in enumerate(cpu_percent)]) + "\n"

                # Ghi dữ liệu vào file
                f.write(f"Time: {time_}")
                f.write(ram_info)
                f.write(cpu_info)
                f.write("\n")
                
                # Chờ một khoảng thời gian
                time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("Stopped monitor")

if __name__ == "__main__":
    monitor_and_log()

