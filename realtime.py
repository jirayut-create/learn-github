from ctypes import *
import os
import time

def load_dll(dll_path):
    """ โหลด DLL และกำหนดพารามิเตอร์ให้กับฟังก์ชัน """
    if not os.path.exists(dll_path):
        print(f"❌ File not found: {dll_path}")
        return None
    try:
        dll = cdll.LoadLibrary(dll_path)
        dll.Connect.argtypes = [c_char_p]
        dll.Connect.restype = c_void_p
        dll.GetRTLogExt.argtypes = [c_void_p, c_char_p, c_int]
        dll.GetRTLogExt.restype = c_int

        dll.Disconnect.argtypes = [c_void_p]
        return dll
    except Exception as e:
        print(f"❌ Error loading DLL: {str(e)}")
        return None

def connect_device(dll, ip, port, timeout=5000, password=""):
    """ เชื่อมต่ออุปกรณ์ """
    parameters = f"protocol=TCP,ipaddress={ip},port={port},timeout={timeout},passwd={password}"
    handle = dll.Connect(parameters.encode('utf-8'))
    if not handle or handle == 0:
        raise ConnectionError("Failed to connect to device")
    return handle

def parse_rtlog(log_data):
    """ แปลงข้อมูลเหตุการณ์แบบเรียลไทม์ให้อ่านง่าย """
    logs = log_data.strip().split("\r\n")  # แยกหลายบันทึก
    parsed_logs = []

    for log in logs:
        fields = log.split("\t")
        log_dict = {}
        for field in fields:
            key_value = field.split("=")
            if len(key_value) == 2:
                log_dict[key_value[0]] = key_value[1]
        
        # แปลงค่า event
        event_type = int(log_dict.get("event", -1))
        event_desc = {
            5: "เข้า",
            6: "ออก",
            200: "ประตูเปิด",
            201: "ประตูปิด"
        }.get(event_type, "ไม่ทราบเหตุการณ์")

        # แปลงค่า inoutstatus
        inout_status = int(log_dict.get("inoutstatus", -1))
        inout_desc = {0: "เข้า", 1: "ออก", 2: "ไม่มี"}.get(inout_status, "ไม่ทราบ")

        log_dict["event_desc"] = event_desc
        log_dict["inout_desc"] = inout_desc
        parsed_logs.append(log_dict)
    
    return parsed_logs

def get_real_time_logs(dll, handle):
    """ ดึงข้อมูลเหตุการณ์แบบเรียลไทม์ """
    buffer_size = 8192
    buffer = create_string_buffer(buffer_size)

    print("📡 Starting real-time monitoring...")
    try:
        while True:
            result = dll.GetRTLogExt(handle, buffer, buffer_size)

            if result > 0:
                log_data = buffer.value.decode('utf-8')
                parsed_logs = parse_rtlog(log_data)
                
                for log in parsed_logs:
                    print(f"📍 Event: {log}")
            elif result == 0:
                time.sleep(0.5)
            else:
                print(f"❌ Error fetching real-time logs. Code: {result}")
                break
    except KeyboardInterrupt:
        print("⏹️ Stopping real-time monitoring.")

def disconnect_device(dll, handle):
    dll.Disconnect(handle)
    print("🔌 Disconnected.")
    
    

def main():
    dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"
    dll = load_dll(dll_path)
    
    if not dll:
        return
    
    try:
        handle = connect_device(dll, "192.168.1.222", 14370)
        get_real_time_logs(dll, handle)  # ดึงข้อมูลแบบเรียลไทม์
    finally:
        disconnect_device(dll, handle)

if __name__ == "__main__":
    main()
