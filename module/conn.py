from ctypes import *
import os

dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"

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
        dll.SetDeviceData.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
        dll.SetDeviceData.restype = c_int
        dll.ControlDevice.argtypes = [c_void_p, c_long, c_long, c_long, c_long, c_long, c_char_p]
        dll.ControlDevice.restype = c_long
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

def disconnect_device(dll, handle):
    dll.Disconnect.argtypes = [c_void_p]
    dll.Disconnect(handle)