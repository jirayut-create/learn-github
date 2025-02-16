import ctypes
import os
import logging
import time

# ตั้งค่า logging (แสดงเฉพาะข้อความ INFO และ ERROR)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# กำหนดตำแหน่งของ plcommpro.dll
DLL_PATH = os.path.join(os.getcwd(), "plcommpro.dll")
if not os.path.exists(DLL_PATH):
    raise FileNotFoundError(f"Cannot find the DLL file at: {DLL_PATH}")

# โหลด DLL และจัดการข้อผิดพลาด
try:
    plcommpro = ctypes.CDLL(DLL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load DLL: {e}")

# กำหนดประเภทของฟังก์ชันที่ใช้ใน DLL
plcommpro.Connect.argtypes = [ctypes.c_char_p]
plcommpro.Connect.restype = ctypes.c_void_p

plcommpro.GetRTLog.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
plcommpro.GetRTLog.restype = ctypes.c_int

plcommpro.Disconnect.argtypes = [ctypes.c_void_p]
plcommpro.Disconnect.restype = ctypes.c_int

def connect_device(connection_params):
    """
    เชื่อมต่ออุปกรณ์โดยใช้พารามิเตอร์การเชื่อมต่อ
    """
    logging.info("Attempting to connect to the device...")
    handle = plcommpro.Connect(connection_params.encode('utf-8'))
    if handle:
        logging.info("Connected to the device successfully.")
        return handle
    else:
        logging.error("Failed to connect to the device. Please check the connection parameters.")
        return None

def disconnect_device(handle):
    """
    ตัดการเชื่อมต่ออุปกรณ์
    """
    try:
        result = plcommpro.Disconnect(handle)
        if result == 0:
            logging.info("Disconnected from the device successfully.")
        else:
            logging.error("Failed to disconnect from the device.")
    except Exception as e:
        logging.error(f"Error during disconnecting: {e}")

def parse_event_log(log_data):
    """
    แปลงข้อมูลเหตุการณ์ให้อยู่ในรูปแบบที่เข้าใจง่าย
    """
    fields = log_data.split(',')
    if len(fields) < 7:
        logging.error("Invalid log data format.")
        return None

    try:
        timestamp, event_type, pin, verified, door, event, inout = fields
        return {
            "timestamp": timestamp,
            "event_type": event_type,
            "pin": pin,
            "verified": verified,
            "door": door,
            "event": event,
            "inout": inout,
        }
    except Exception as e:
        logging.error(f"Error parsing log data: {e}")
        return None

def monitor_real_time_logs(handle):
    buffer_size = 4096  # เพิ่มขนาดบัฟเฟอร์เพื่อรองรับข้อมูลที่ใหญ่ขึ้น
    buffer = ctypes.create_string_buffer(buffer_size)
    previous_log_data = None
    logging.info("Starting real-time event monitoring... Press Ctrl+C to stop.")
    try:
        while True:
            result = plcommpro.GetRTLog(handle, buffer, buffer_size)
            if result > 0:
                log_data = buffer.value.decode('utf-8', errors='ignore')  # เพิ่ม errors='ignore' เพื่อจัดการข้อผิดพลาดในการถอดรหัส
                for record in log_data.split('\r\n'):  # แยกแต่ละเหตุการณ์
                    if not record.strip():
                        continue
                    if "type=rtlog" in record:
                        # ข้อมูลเหตุการณ์แบบเรียลไทม์
                        parsed_record = parse_rtlog_ext(record)
                        logging.info(f"Real-time event detected: {parsed_record}")
                    elif "type=rtstate" in record:
                        # ข้อมูลสถานะประตูและสัญญาณเตือน
                        parsed_record = parse_rtlog_ext(record)
                        logging.info(f"Door/Alarm status detected: {parsed_record}")
                    else:
                        # ข้อมูลในรูปแบบปกติ (GetRTLog)
                        event_data = parse_event_log(record)
                        if event_data:
                            logging.info(f"Event detected: {event_data}")
                            if event_data["pin"] != "0":
                                logging.info(f"Card detected: {event_data['pin']}")
            elif result == 0:
                logging.info("No new events. Waiting...")
                time.sleep(0.1)
            else:
                logging.error(f"Error occurred while fetching real-time logs. Result code: {result}")
                break
    except KeyboardInterrupt:
        logging.info("Real-time monitoring stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error during monitoring: {e}")
    finally:
        logging.info("Real-time monitoring has ended.")



def parse_real_time_event(log_data):
    """
    แยกข้อมูลเหตุการณ์แบบเรียลไทม์
    """
    fields = log_data.split(',')
    if len(fields) < 7:
        logging.error(f"Invalid real-time event data: {log_data}")
        return None
    try:
        timestamp = fields[0]
        pin = fields[1]
        cardno = fields[2]
        eventaddr = fields[3]
        event = fields[4]
        inoutstatus = fields[5]
        verifytype = fields[6]
        return {
            "timestamp": timestamp,
            "pin": pin,
            "cardno": cardno,
            "eventaddr": eventaddr,
            "event": event,
            "inoutstatus": inoutstatus,
            "verifytype": verifytype,
        }
    except Exception as e:
        logging.error(f"Error parsing real-time event data: {e}. Log data: {log_data}")
        return None

def parse_door_alarm_status(log_data):
    """
    แยกข้อมูลสถานะประตูและสัญญาณเตือน
    """
    fields = log_data.split(',')
    if len(fields) < 3:
        logging.error(f"Invalid door/alarm status data: {log_data}")
        return None
    try:
        timestamp = fields[0]
        sensor_status = int(fields[1])
        alarm_status = int(fields[2])
        return {
            "timestamp": timestamp,
            "sensor_status": sensor_status,
            "alarm_status": alarm_status,
        }
    except Exception as e:
        logging.error(f"Error parsing door/alarm status data: {e}. Log data: {log_data}")
        return None

def parse_rtlog_ext(log_data):
    records = log_data.split('\r\n')
    parsed_records = []
    for record in records:
        if not record:
            continue
        try:
            if record.startswith("type=rtlog"):
                fields = record.split('\t')
                parsed_record = {
                    "type": fields[0].split('=')[1],
                    "time": fields[1].split('=')[1],
                    "pin": fields[2].split('=')[1],
                    "cardno": fields[3].split('=')[1],
                    "eventaddr": fields[4].split('=')[1],
                    "event": fields[5].split('=')[1],
                    "inoutstatus": fields[6].split('=')[1],
                    "verifytype": fields[7].split('=')[1],
                }
                parsed_records.append(parsed_record)
            elif record.startswith("type=rtstate"):
                fields = record.split('\t')
                parsed_record = {
                    "type": fields[0].split('=')[1],
                    "time": fields[1].split('=')[1],
                    "sensor": fields[2].split('=')[1],
                    "relay": fields[3].split('=')[1],
                    "alarm": fields[4].split('=')[1],
                }
                parsed_records.append(parsed_record)
        except Exception as e:
            logging.error(f"Error parsing record: {record}. Error: {e}")
    return parsed_records

def check_device_status(handle):
    """
    ตรวจสอบสถานะของอุปกรณ์
    """
    try:
        buffer_size = 1024
        buffer = ctypes.create_string_buffer(buffer_size)
        result = plcommpro.GetDeviceStatus(handle, buffer, buffer_size)
        if result == 0:
            logging.info(f"Device status: {buffer.value.decode('utf-8')}")
        else:
            logging.error(f"Failed to get device status. Error code: {result}")
    except Exception as e:
        logging.error(f"Error checking device status: {e}")

plcommpro.GetRTLogExt.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
plcommpro.GetRTLogExt.restype = ctypes.c_int

def monitor_real_time_logs_ext(handle):
    buffer_size = 8192  # Increased buffer size
    buffer = ctypes.create_string_buffer(buffer_size)
    logging.info("Starting real-time event monitoring with GetRTLogExt... Press Ctrl+C to stop.")
    try:
        while True:
            result = plcommpro.GetRTLogExt(handle, buffer, buffer_size)
            if result > 0:
                log_data = buffer.value.decode('utf-8', errors='ignore')
                logging.debug(f"Raw log data: {log_data}")  # Log raw data for debugging
                if not log_data.strip():
                    logging.warning("Received empty log data.")
                    continue
                parsed_records = parse_rtlog_ext(log_data)
                if not parsed_records:
                    logging.warning("Failed to parse log data.")
                    continue
                for record in parsed_records:
                    logging.info(f"Event detected: {record}")
            elif result == 0:
                logging.info("No new events. Waiting...")
                time.sleep(0.1)
            else:
                logging.error(f"Error occurred while fetching real-time logs. Result code: {result}")
                break
    except KeyboardInterrupt:
        logging.info("Real-time monitoring stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error during monitoring: {e}")
    finally:
        logging.info("Real-time monitoring has ended.")

# Define argument types for ControlDevice
plcommpro.ControlDevice.argtypes = [
    ctypes.c_void_p,  # handle
    ctypes.c_long,    # OperationID
    ctypes.c_long,    # Param1
    ctypes.c_long,    # Param2
    ctypes.c_long,    # Param3
    ctypes.c_long,    # Param4
    ctypes.c_char_p   # Options
]
plcommpro.ControlDevice.restype = ctypes.c_int

def enable_real_time_mode(handle):
    """
    เปิดใช้งานโหมดการดึงข้อมูลเหตุการณ์แบบเรียลไทม์
    """
    try:
        command = "REALTIME=ON"
        logging.debug(f"Calling ControlDevice with: "
                      f"handle={handle}, "
                      f"OperationID=9, "
                      f"Param1=0, "
                      f"Param2=0, "
                      f"Param3=0, "
                      f"Param4=0, "
                      f"Options={command}")
        result = plcommpro.ControlDevice(
            handle,                  # Handle (void*)
            ctypes.c_long(9),       # OperationID (9 for enabling real-time mode)
            ctypes.c_long(0),       # Param1
            ctypes.c_long(0),       # Param2
            ctypes.c_long(0),       # Param3
            ctypes.c_long(0),       # Param4
            command.encode('utf-8') # Options
        )

        if result == 0:
            logging.info("Real-time mode enabled successfully.")
        else:
            logging.error(f"Failed to enable real-time mode. Error code: {result}")
    except Exception as e:
        logging.error(f"Error enabling real-time mode: {e}")

if __name__ == "__main__":
    # พารามิเตอร์การเชื่อมต่อ (ปรับตามอุปกรณ์ของคุณ)
    ip_address = "192.168.1.222"
    port = "14370"
    password = ""
    connection_params = f"protocol=TCP,ipaddress={ip_address},port={port},timeout=2000,passwd={password}"
    # เชื่อมต่ออุปกรณ์
    device_handle = connect_device(connection_params)
    if device_handle:
        try:

            enable_real_time_mode(device_handle)
            monitor_real_time_logs_ext(device_handle)
        finally:
            # ตัดการเชื่อมต่อเมื่อเสร็จสิ้น
            disconnect_device(device_handle)