from ctypes import cdll, c_char_p, c_int, c_void_p, create_string_buffer
import os
import logging
import time

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# โหลด DLL
dll_path = r"C:\dev-zkaccess\Pull_SDK\plcommpro.dll"
if not os.path.exists(dll_path):
    logging.error(f"❌ Error: File not found - {dll_path}")
    exit()

zkemkeeper = cdll.LoadLibrary(dll_path)

# ตั้งค่าการเชื่อมต่อ
parameters = "protocol=TCP,ipaddress=192.168.1.222,port=14370,timeout=5000,passwd="
zkemkeeper.Connect.argtypes = [c_char_p]
zkemkeeper.Connect.restype = c_void_p

connection_handle = zkemkeeper.Connect(parameters.encode("utf-8"))
if not connection_handle or connection_handle == 0:
    logging.error("❌ Connection failed!")
    exit()
else:
    logging.info(f"✅ เชื่อมต่ออุปกรณ์สำเร็จ! Connection handle: {connection_handle}")

# กำหนดฟังก์ชัน GetRTLog
zkemkeeper.GetRTLog.argtypes = [c_void_p, c_char_p, c_int]
zkemkeeper.GetRTLog.restype = c_int

def parse_rtlog_data(data):
    """
    แปลงข้อมูลที่ได้รับจาก GetRTLog เป็น Dictionary
    """
    records = data.strip().split("\r\n")
    parsed_records = []
    
    for record in records:
        fields = record.split(",")
        
        if len(fields) < 6:
            continue
        
        # ตรวจสอบว่าบันทึกเป็นสถานะประตูหรือเหตุการณ์แบบเรียลไทม์
        if fields[3] == "255":
            log_type = "door_status"
            event_data = {
                "timestamp": fields[1],
                "door_sensor_status": fields[2],
                "alarm_status": fields[4]
            }
        else:
            log_type = "event"
            event_data = {
                "timestamp": fields[0],
                "pin": fields[1],
                "card_no": fields[2],
                "event_addr": fields[3],
                "event_code": fields[4],
                "in_out_status": fields[5],
                "verify_type": fields[6]
            }
        
        parsed_records.append({"type": log_type, "data": event_data})

    return parsed_records


MAX_BUFFER_SIZE = 1048576  # 1 MB
def reconnect(device):
    logging.info("⌛ กำลังเชื่อมต่อใหม่...")
    device.disconnect()
    time.sleep(5)  # รอสักครู่ก่อนเชื่อมต่อใหม่
    if device.connect():
        logging.info("✅ เชื่อมต่อใหม่สำเร็จ")
        return True
    else:
        logging.error("❌ ไม่สามารถเชื่อมต่อใหม่ได้")
        return False

def get_real_time_logs(device):
    buffer_size = 65536  # ขนาด buffer เริ่มต้น 64 KB
    buffer = create_string_buffer(buffer_size)

    while True:
        try:
            if not device.connection_handle or device.connection_handle == 0:
                logging.error("❌ Connection handle ไม่ถูกต้อง")
                if not reconnect(device):
                    break

            result = zkemkeeper.GetRTLog(device.connection_handle, buffer, buffer_size)
            if result > 0:
                log_data = buffer.value.decode('utf-8', errors='ignore')
                logs = parse_rtlog_data(log_data)
                
                for log in logs:
                    logging.info(f"📌 Log Received: {log}")
            elif result == 0:
                logging.info("⏳ No new log. Waiting...")
            elif result == -104:
                if buffer_size < MAX_BUFFER_SIZE:
                    buffer_size *= 2  # เพิ่มขนาด buffer เป็นสองเท่า
                    buffer = create_string_buffer(buffer_size)
                    logging.warning(f"⚠️ Buffer เต็ม! ปรับขนาด buffer เป็น {buffer_size} bytes")
                else:
                    logging.error("⚠️ Buffer เต็มและถึงขนาดสูงสุดแล้ว! ไม่สามารถปรับขนาด buffer เพิ่มได้")
                    break
            else:
                logging.error(f"⚠️ Error fetching logs. Error Code: {result}")
                if not reconnect(device):
                    break
            time.sleep(0.5)  # ลดเวลา sleep เพื่อดึงข้อมูลบ่อยขึ้น
        except KeyboardInterrupt:
            logging.info("🛑 หยุดการทำงานโดยผู้ใช้")
            break
        except Exception as e:
            logging.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
            if not reconnect(device):
                break

try:
    get_real_time_logs(connection_handle)
except KeyboardInterrupt:
    logging.info("🛑 Monitoring stopped by user.")
finally:
    zkemkeeper.Disconnect.argtypes = [c_void_p]
    zkemkeeper.Disconnect(connection_handle)
    logging.info("🔌 ปิดการเชื่อมต่อสำเร็จ!")
    
    

