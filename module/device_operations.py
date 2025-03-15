from ctypes import *
import os

def load_dll(dll_path):
    if not os.path.exists(dll_path):
        print(f"\u274c File not found: {dll_path}")
        return None
    try:
        dll = cdll.LoadLibrary(dll_path)
        dll.Connect.argtypes = [c_char_p]
        dll.Connect.restype = c_void_p
        dll.DeleteDeviceData.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
        dll.DeleteDeviceData.restype = c_int
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

def delete_transaction_data(dll, handle):
    """
    ลบข้อมูลทั้งหมดในตาราง transaction
    """
    table_name = "transaction"
    data = ""  # ค่าว่างเพื่อลบทุกข้อมูลในตาราง
    options = ""  # ค่าดีฟอลต์

    result = dll.DeleteDeviceData(
        handle,
        table_name.encode('utf-8'),
        data.encode('utf-8'),
        options.encode('utf-8')
    )

    if result == 0:
        print("\u2705 All data in table 'transaction' has been deleted.")
    else:
        print(f"\u274c Failed to delete data. Error Code: {result}")

def disconnect_device(dll, handle):
    dll.Disconnect.argtypes = [c_void_p]
    dll.Disconnect(handle)