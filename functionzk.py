from ctypes import *
import os


def load_dll(dll_path):
    if not os.path.exists(dll_path):
        print(f"\u274c File not found: {dll_path}")
        return  None
    try:
        dll = cdll.LoadLibrary(dll_path)
        dll.Connect.argtypes = [c_char_p]
        dll.Connect.restype = c_void_p
        dll.GetDeviceData.argtypes = [c_void_p, c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_char_p]
        dll.GetDeviceData.restype = c_int
        dll.ControlDevice.argtypes = [c_void_p, c_long, c_long, c_long, c_long, c_long, c_char_p]
        dll.ControlDevice.restype = c_long
        dll.Disconnect.argtypes = [c_void_p]
        return dll
    except Exception as e:
        print(f"\u274c Error loading DLL: {str(e)}")
        return None

def connect_device(dll, ip, port, timeout=5000, password=""):
    parameters = f"protocol=TCP,ipaddress={ip},port={port},timeout={timeout},passwd={password}"
    dll.Connect.argtypes = [c_char_p]
    dll.Connect.restype = c_void_p
    handle = dll.Connect(parameters.encode('utf-8'))
    if not handle or handle == 0:
        raise ConnectionError("Failed to connect to device")
    return handle

def control_door(dll, handle, door_id=1, open_time=5):
    operation_id = 1  # Control lock
    output_type = 1  # Lock operation
    reserved = 0
    options = c_char_p(b"")
    
    dll.ControlDevice.argtypes = [c_void_p, c_long, c_long, c_long, c_long, c_long, c_char_p]
    dll.ControlDevice.restype = c_long
    
    result = dll.ControlDevice(handle, operation_id, door_id, output_type, open_time, reserved, options)
    if result < 0:
        raise RuntimeError(f"Failed to open door {door_id}, Error Code: {result}")
    # print(f"🚪✅ Door {door_id} opened successfully!")

def get_device_data(dll, handle, table_name, field_names="*", filter_conditions="", options=""):
    """
    ดึงข้อมูลจากอุปกรณ์ผ่านฟังก์ชัน GetDeviceData
    """
    buffer_size = 64 * 1024
    buffer = create_string_buffer(buffer_size)
    result = dll.GetDeviceData(
        handle, buffer, buffer_size,
        table_name.encode('utf-8'), field_names.encode('utf-8'),
        filter_conditions.encode('utf-8'), options.encode('utf-8')
    )
    if result >= 0:
        data = buffer.value.decode('utf-8').strip()
        return data if data else f"\u26A0 No data found in table: {table_name}"
    else:
        return f"\u274c Error! Code: {result}"

def fetch_data_from_tables(dll, handle, tables):
    """
    ดึงข้อมูลจากตารางต่าง ๆ
    """
    for table in tables:
        print(f"\nTrying to fetch data from table: {table}")
        data = get_device_data(dll, handle, table)
        print(f"[Data from {table}]\n", data)
        if not data.startswith("\u274c"):
            break

def fetch_data(dll, handle, tables):
    """
    ดึงข้อมูลจากตารางต่าง ๆ
    """
    for table in tables:
        print(f"\nTrying to fetch data from table: {table}")
        data = get_device_data(dll, handle, table)
        print(f"[Data from {table}]\n", data)
        if not data.startswith("\u274c"):
            break


def disconnect_device(dll, handle):
    dll.Disconnect.argtypes = [c_void_p]
    dll.Disconnect(handle)

# def main():
#     try:
#         dll = load_dll(dll_path)
#         handle = connect_device(dll, "192.168.1.202", 14370)
#         print(f"✅ Connected successfully! Handle: {handle}")
#         control_door(dll, handle, door_id=1, open_time=5)
#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if 'handle' in locals():
#             disconnect_device(dll, handle)
#             # print("🔌 Disconnected.")



# dll = load_dll(dll_path)
# handle = connect_device(dll, "192.168.1.222", 14370)

# control_door(dll, handle, door_id=4, open_time=5)
# disconnect_device(dll, handle)
# print("🔌 Disconnected.")