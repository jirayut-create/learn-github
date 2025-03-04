import ctypes
import os
import logging
import time

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# กำหนดตำแหน่งของ plcommpro.dll
DLL_PATH = os.path.join(os.getcwd(), "plcommpro.dll")
if not os.path.exists(DLL_PATH):
    raise FileNotFoundError(f"Cannot find the DLL file at: {DLL_PATH}")

# โหลด DLL
try:
    plcommpro = ctypes.CDLL(DLL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load DLL: {e}")

# กำหนดประเภทของฟังก์ชันที่ใช้ใน DLL
plcommpro.Connect.argtypes = [ctypes.c_char_p]
plcommpro.Connect.restype = ctypes.c_void_p

plcommpro.GetRTLogExt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
plcommpro.GetRTLogExt.restype = ctypes.c_int

plcommpro.Disconnect.argtypes = [ctypes.c_void_p]
plcommpro.Disconnect.restype = ctypes.c_int

plcommpro.ControlDevice.argtypes = [ctypes.c_void_p, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_long, ctypes.c_char_p]
plcommpro.ControlDevice.restype = ctypes.c_int

def connect_device(connection_params):
    """ เชื่อมต่ออุปกรณ์ """
    logging.info("🔌 Connecting to the device...")
    handle = plcommpro.Connect(connection_params.encode('utf-8'))
    if handle:
        logging.info("✅ Device connected successfully.")
        return handle
    else:
        logging.error("❌ Failed to connect to the device. Please check the connection parameters.")
        return None

def disconnect_device(handle):
    """ ตัดการเชื่อมต่ออุปกรณ์ """
    try:
        result = plcommpro.Disconnect(handle)
        if result == 0:
            logging.info("🔌 Disconnected successfully.")
        else:
            logging.error("❌ Failed to disconnect.")
    except Exception as e:
        logging.error(f"Error during disconnecting: {e}")

def check_connection(handle):
    """ ตรวจสอบการเชื่อมต่อของอุปกรณ์ """
    buffer = ctypes.create_string_buffer(64)
    result = plcommpro.GetDeviceParam(handle, buffer, 64, b"IPAddress")
    return result >= 0  # ถ้าค่า >= 0 แสดงว่าอุปกรณ์ยังออนไลน์

def reconnect_device(connection_params, max_retries=5):
    """ พยายามเชื่อมต่อใหม่สูงสุด max_retries ครั้ง """
    for attempt in range(1, max_retries + 1):
        logging.info(f"🔄 Reconnecting... Attempt {attempt}/{max_retries}")
        handle = connect_device(connection_params)
        if handle:
            return handle
        time.sleep(5)  # รอ 5 วินาทีก่อนลองใหม่
    logging.error("❌ Failed to reconnect after multiple attempts.")
    return None

def open_door(handle, door_id):
    """ เปิดประตูตาม ID ที่กำหนด """
    try:
        operation_id = 1  # คำสั่งเปิดประตู
        param1 = door_id
        param2 = 1  # Lock Output
        param3 = 1  # เปิด 1 วินาที
        result = plcommpro.ControlDevice(handle, operation_id, param1, param2, param3, 0, "".encode('utf-8'))
        if result == 0:
            logging.info(f"🚪 Door {door_id} opened successfully.")
        else:
            logging.error(f"❌ Failed to open door {door_id}. Error code: {result}")
    except Exception as e:
        logging.error(f"Error opening door {door_id}: {e}")

def parse_rtlog_ext(log_data):
    """ แปลงข้อมูลเหตุการณ์จาก GetRTLogExt ให้อ่านง่าย """
    logs = log_data.strip().split("\r\n")
    parsed_logs = []

    for log in logs:
        fields = log.split("\t")
        log_dict = {}
        for field in fields:
            key_value = field.split("=")
            if len(key_value) == 2:
                log_dict[key_value[0]] = key_value[1]
        
        parsed_logs.append(log_dict)
    
    return parsed_logs

def monitor_real_time_logs(handle, target_card_numbers, connection_params):
    """ ดึงข้อมูลเหตุการณ์แบบเรียลไทม์จากอุปกรณ์ """
    buffer_size = 64 * 1024
    buffer = ctypes.create_string_buffer(buffer_size)

    logging.info("📡 Monitoring real-time logs... Press Ctrl+C to stop.")
    
    try:
        while True:
            if not check_connection(handle):
                logging.warning("⚠️ Connection lost! Trying to reconnect...")
                handle = reconnect_device(connection_params)
                if not handle:
                    break  # ถ้าเชื่อมต่อใหม่ไม่ได้ ให้หยุด

            result = plcommpro.GetRTLogExt(handle, buffer, buffer_size)
            if result > 0:
                log_data = buffer.value.decode('utf-8').strip()
                event_logs = parse_rtlog_ext(log_data)

                for event in event_logs:
                    if event.get("pin") == "0":
                        continue  # ข้ามรายการที่ไม่ต้องการ

                    logging.info(f"📍 Event detected: {event}")

                    if event["pin"] in target_card_numbers:
                        logging.info(f"🎯 Target card detected: {event['pin']}. Processing door operation...")

                        try:
                            if event["verifytype"] == "1":
                                open_door(handle, door_id=1)  # เปิดประตู 1
                            elif event["verifytype"] == "2":
                                open_door(handle, door_id=2)  # เปิดประตู 2
                            else:
                                logging.warning(f"Unknown verify type: {event['verifytype']}. No door opened.")
                        except Exception as e:
                            logging.error(f"Error processing door operation: {e}")

                        time.sleep(0.1)  # หน่วงเวลา 0.1 วินาที
            elif result == 0:
                logging.info("⚠️ No new events.")
                time.sleep(0.5)
            else:
                logging.error(f"❌ Error fetching real-time logs. Code: {result}")
                break
    except KeyboardInterrupt:
        logging.info("⏹️ Monitoring stopped by user.")
    finally:
        logging.info("🔌 Real-time monitoring ended.")

if __name__ == "__main__":
    ip_address = "192.168.1.222"
    port = "14370"
    password = ""

    connection_params = f"protocol=TCP,ipaddress={ip_address},port={port},timeout=2000,passwd={password}"

    target_card_numbers = ["51392", "1111", "7668839", "7668835"]

    device_handle = connect_device(connection_params)
    if device_handle:
        try:
            monitor_real_time_logs(device_handle, target_card_numbers, connection_params)
        finally:
            disconnect_device(device_handle)
            logging.info("🔌 Device disconnected.")
