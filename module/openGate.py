from ctypes import *
import os

def control_door(dll, handle, door_id, open_time):
    operation_id = 1  # Control lock
    output_type = 1  # Lock operation
    reserved = 0
    options = c_char_p(b"")
    
    dll.ControlDevice.argtypes = [c_void_p, c_long, c_long, c_long, c_long, c_long, c_char_p]
    dll.ControlDevice.restype = c_long
    
    result = dll.ControlDevice(handle, operation_id, door_id, output_type, open_time, reserved, options)
    if result < 0:
        raise RuntimeError(f"Failed to open door {door_id}, Error Code: {result}")
    print(f"🚪✅ Door {door_id} opened successfully!")