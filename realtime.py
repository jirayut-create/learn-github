import ctypes
import os
import logging
import time
from typing import List, Optional, Tuple

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

plcommpro.Disconnect.argtypes = [ctypes.c_void_p]
plcommpro.Disconnect.restype = None

plcommpro.PullLastError.argtypes = []
plcommpro.PullLastError.restype = ctypes.c_int

plcommpro.GetDeviceData.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
plcommpro.GetDeviceData.restype = ctypes.c_int

plcommpro.SetDeviceData.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_char_p]
plcommpro.SetDeviceData.restype = ctypes.c_int

plcommpro.DeleteDeviceData.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
plcommpro.DeleteDeviceData.restype = ctypes.c_int

plcommpro.ControlDevice.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
plcommpro.ControlDevice.restype = ctypes.c_int

plcommpro.GetDeviceParam.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_int, ctypes.c_char_p]
plcommpro.GetDeviceParam.restype = ctypes.c_int

plcommpro.GetRTLog.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_byte), ctypes.c_int]
plcommpro.GetRTLog.restype = ctypes.c_int


class AccessPanel:
    def __init__(self):
        self._handle = None
        self._fail_count = 0
        self._last_event_time = "0000-00-00 00:00:00"

    def get_last_error(self) -> int:
        return plcommpro.PullLastError()

    def is_connected(self) -> bool:
        if self._handle:
            if self._fail_count > 5:
                self._fail_count = 0
                self.disconnect()
                return False
            return True
        return False

    def disconnect(self):
        if self.is_connected():
            plcommpro.Disconnect(self._handle)
            self._handle = None

    def connect(self, ip: str, port: int, key: int, timeout: int) -> bool:
        if self.is_connected():
            return False

        conn_str = f"protocol=TCP,ipaddress={ip},port={port},timeout={timeout},passwd={key if key != 0 else ''}"
        self._handle = plcommpro.Connect(conn_str.encode('utf-8'))
        return self._handle is not None

    def get_fingerprint(self, pin: str, finger: int) -> Optional[dict]:
        if not self.is_connected():
            return None

        buffer = (ctypes.c_byte * 2 * 1024 * 1024)()
        field_names = "Size\tPin\tFingerID\tValid\tTemplate\tEndTag"
        filter_str = f"Pin={pin},FingerID={finger},Valid=1"
        read_result = plcommpro.GetDeviceData(self._handle, buffer, len(buffer), b"templatev10", field_names.encode('utf-8'), filter_str.encode('utf-8'), b"")

        if read_result >= 0:
            log_data = bytearray(buffer).decode('utf-8').strip('\x00')
            # Parse log_data here (similar to FpReader in C#)
            # This is a placeholder for parsing logic
            return {"pin": pin, "finger": finger, "template": "parsed_template"}
        else:
            self._fail_count += 1
            return None

    def read_users(self) -> Optional[List[dict]]:
        if not self.is_connected():
            return None

        buffer = (ctypes.c_byte * 20 * 1024 * 1024)()
        read_result = plcommpro.GetDeviceData(self._handle, buffer, len(buffer), b"user", b"*", b"", b"")

        if read_result >= 0:
            log_data = bytearray(buffer).decode('utf-8').strip('\x00')
            # Parse log_data here (similar to UsersReader in C#)
            # This is a placeholder for parsing logic
            users = [{"pin": "123", "name": "John Doe"}]  # Example data
            return users
        else:
            self._fail_count += 1
            return None

    def delete_user(self, pin: str) -> bool:
        if not self.is_connected():
            return False

        if plcommpro.DeleteDeviceData(self._handle, b"user", f"Pin={pin}".encode('utf-8'), b"") >= 0:
            return True
        else:
            self._fail_count += 1
            return False

    def open_door(self, door_id: int, seconds: int) -> bool:
        if not self.is_connected() or seconds < 1 or seconds > 60:
            return False

        if plcommpro.ControlDevice(self._handle, 1, door_id, 1, seconds, 0, b"") >= 0:
            return True
        else:
            self._fail_count += 1
            return False

    def close_door(self, door_id: int) -> bool:
        if not self.is_connected():
            return False

        if plcommpro.ControlDevice(self._handle, 1, door_id, 1, 0, 0, b"") >= 0:
            return True
        else:
            self._fail_count += 1
            return False

    def get_door_count(self) -> int:
        if not self.is_connected():
            return -1

        buffer = (ctypes.c_byte * 2048)()
        if plcommpro.GetDeviceParam(self._handle, buffer, len(buffer), b"LockCount") >= 0:
            lock_count_str = bytearray(buffer).decode('utf-8').strip('\x00').replace("LockCount=", "")
            try:
                return int(lock_count_str)
            except ValueError:
                return -1
        else:
            self._fail_count += 1
            return -1

    def get_event_log(self) -> Optional[dict]:
        if not self.is_connected():
            print('1')
            return None

    # สร้าง buffer ด้วย ctypes และใช้ ctypes.cast เพื่อแปลงเป็นพอยน์เตอร์
        buffer_size = 2 * 1024 * 1024  # ขนาด buffer
        buffer = (ctypes.c_byte * buffer_size)()  # สร้างอาร์เรย์ของ c_byte
        buffer_ptr = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte))  # แปลงเป็นพอยน์เตอร์

        if plcommpro.GetRTLog(self._handle, buffer_ptr, buffer_size) >= 0:
            log_data = bytearray(buffer).decode('utf-8').strip('\x00')
            events = log_data.split("\r\n")
            parsed_events = []
            for event in events:
                if event:
                    parts = event.split(',')
                    if len(parts) == 7:
                        parsed_events.append({
                            "timestamp": parts[0],
                            "pin": parts[1],
                            "card": parts[2],
                            "event_type": parts[3],
                            "door": parts[4],
                            "inout": parts[5],
                            "verified": parts[6]
                        })
            return {"events": parsed_events}
        else:
            self._fail_count += 1
            print('2')
            return None


if __name__ == "__main__":
    panel = AccessPanel()
    if panel.connect("192.168.1.222", 14370, 0, 2000):
        try:
            event_log = panel.get_event_log()
            if event_log:
                logging.info(f"Event Log: {event_log}")
        finally:
            panel.disconnect()

# if __name__ == "__main__":
#     panel = AccessPanel()
#     if panel.connect("192.168.1.222", 14370, 0, 2000):
#         try:
#             # users = panel.read_users()
#             # if users:
#             #     logging.info(f"Users: {users}")

#             event_log = panel.get_event_log()
#             if event_log:
#                 logging.info(f"Event Log: {event_log}")

#             panel.open_door(1, 5)  # Open door 1 for 5 seconds
#             time.sleep(5)
#             panel.close_door(1)  # Close door 1
#         finally:
#             panel.disconnect()