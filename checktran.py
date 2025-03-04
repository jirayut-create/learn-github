from ctypes import *
import os

def load_dll(dll_path):
    """ โหลด DLL และกำหนดพารามิเตอร์ให้กับฟังก์ชัน """
    if not os.path.exists(dll_path):
        print(f"❌ File not found: {dll_path}")
        return None
    try:
        dll = cdll.LoadLibrary(dll_path)
        dll.Connect.argtypes = [c_char_p]
        dll.Connect.restype = c_void_p
        dll.GetDeviceParam.argtypes = [c_void_p, c_char_p, c_int, c_char_p]
        dll.GetDeviceParam.restype = c_int
        dll.SetDeviceParam.argtypes = [c_void_p, c_char_p]
        dll.SetDeviceParam.restype = c_int
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

def get_device_params(dll, handle, param_names):
    """ อ่านค่าพารามิเตอร์ของอุปกรณ์ """
    buffer_size = 1024
    buffer = create_string_buffer(buffer_size)
    
    param_str = ",".join(param_names).encode('utf-8')
    result = dll.GetDeviceParam(handle, buffer, buffer_size, param_str)

    if result >= 0:
        param_values = buffer.value.decode('utf-8').strip()
        param_list = param_values.split(",")

        # แก้ไขการดึงค่าหลัง =
        param_dict = {}
        for param in param_list:
            key_value = param.split("=")
            if len(key_value) == 2:
                param_dict[key_value[0]] = key_value[1]
            else:
                param_dict[key_value[0]] = "N/A"  # ถ้าไม่มีค่าให้ใส่เป็น N/A
        return param_dict
    else:
        print(f"❌ Error fetching device parameters. Code: {result}")
        return None

def enable_transmode(dll, handle):
    """ เปิดโหมดส่งข้อมูลแบบเรียลไทม์ """
    result = dll.SetDeviceParam(handle, b"TransMode=1")
    if result == 0:
        print("✅ TransMode set to 1 (Real-time mode enabled)!")
    else:
        print(f"❌ Failed to enable TransMode. Error: {result}")

def disconnect_device(dll, handle):
    dll.Disconnect(handle)
    print("🔌 Disconnected.")
    
def check_supported_params(dll, handle):
    params = ["TransMode", "DeviceID", "RealTimeEvent", "DoorSensorType"]
    buffer_size = 512
    buffer = create_string_buffer(buffer_size)
    param_str = ",".join(params).encode('utf-8')
    result = dll.GetDeviceParam(handle, buffer, buffer_size, param_str)

    if result >= 0:
        param_values = buffer.value.decode('utf-8').strip()
        print(f"📡 Device Support Check:\n{param_values}")
    else:
        print(f"❌ Error checking parameters. Code: {result}")


def main():
    dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"
    dll = load_dll(dll_path)
    
    if not dll:
        return
    
    try:
        handle = connect_device(dll, "192.168.1.222", 14370)
        check_supported_params(dll, handle)
        dll.SetDeviceParam(handle, b"Reset=1")

        # รายการพารามิเตอร์ที่ต้องการอ่าน
        param_names = ["TransMode", "DeviceID", "DoorSensorType", "LockDriveTime", "CardReadInterval"]
        
        # อ่านค่าพารามิเตอร์
        device_params = get_device_params(dll, handle, param_names)
        if device_params:
            print("📡 Device Parameters:")
            for key, value in device_params.items():
                print(f"🔹 {key}: {value}")

            # ตรวจสอบค่า TransMode
            if device_params.get("TransMode") != "1":
                print("⚠️ TransMode is not set to 1. Updating...")
                enable_transmode(dll, handle)
                
                # ตรวจสอบค่าอีกครั้ง
                device_params = get_device_params(dll, handle, ["TransMode"])
                print(f"🔍 TransMode updated: {device_params.get('TransMode')}")
                
    finally:
        disconnect_device(dll, handle)

if __name__ == "__main__":
    main()
    
