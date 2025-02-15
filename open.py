import sys
import json
from ctypes import c_char_p, c_long, c_void_p
from functionzk import load_dll,connect_device,disconnect_device


def open_doorid(dll, handle, door_id, open_time):
    operation_id = 1  # Control lock
    output_type = 1  # Lock operation
    reserved = 0
    options = c_char_p(b"")
    
    dll.ControlDevice.argtypes = [c_void_p, c_long, c_long, c_long, c_long, c_long, c_char_p]
    dll.ControlDevice.restype = c_long
    
    result = dll.ControlDevice(handle, operation_id, door_id, output_type, open_time, reserved, options)
    if result < 0:
        
        # raise RuntimeError(f"Failed to open door {door_id}, Error Code: {result}")
        return {"status": "fail", "message": "❌ ล้มเหลว: IP ไม่ตรงกัน"}
    return {"status": "success", "message": f"✅ ประตู {door_id} เปิดแล้ว!"}


if __name__ == "__main__":
    # open_door('192.168.1.222','1')
    dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"
    dll = load_dll(dll_path)
    handle = connect_device(dll,"192.168.1.222",14370)
    open_time=5
    # door_id = 1
    
    try:
        if len(sys.argv) > 1:
           
            door = sys.argv[1]
            door_id = int(door)
            
            response = open_doorid(dll, handle, door_id, open_time)
        else:
            response = {"status": "error", "message": "❌ ไม่มีค่า IP ส่งมา"}

        # ✅ พิมพ์เฉพาะ JSON ไม่มีข้อความอื่น
        print(json.dumps(response))
        disconnect_device(dll, handle)

    except Exception as e:
        print(json.dumps({"status": "error", "message": f"❌ เกิดข้อผิดพลาด: {str(e)}"}))
