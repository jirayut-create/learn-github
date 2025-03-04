import ctypes
from ctypes import c_char_p, c_void_p, c_int,c_byte, POINTER, byref
import time
import os
from datetime import datetime



# Load the plcommpro.dll library
DLL_PATH = os.path.join(os.getcwd(), "plcommpro.dll")
if not os.path.exists(DLL_PATH):
    raise FileNotFoundError(f"Cannot find the DLL file at: {DLL_PATH}")

# โหลด DLL
try:
    plcommpro = ctypes.CDLL(DLL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load DLL: {e}")



# Define function prototypes
Connect = plcommpro.Connect
Connect.argtypes = [c_char_p]
Connect.restype = c_void_p

Disconnect = plcommpro.Disconnect
Disconnect.argtypes = [c_void_p]

GetDeviceParam = plcommpro.GetDeviceParam
GetDeviceParam.argtypes = [c_void_p, POINTER(c_byte), c_int, c_char_p]
GetDeviceParam.restype = c_int

SetDeviceParam = plcommpro.SetDeviceParam
SetDeviceParam.argtypes = [c_void_p, c_char_p]
SetDeviceParam.restype = c_int

ControlDevice = plcommpro.ControlDevice
ControlDevice.argtypes = [c_void_p, c_int, c_int, c_int, c_int, c_int, c_char_p]
ControlDevice.restype = c_int

GetRTLog = plcommpro.GetRTLog
GetRTLog.argtypes = [c_void_p, POINTER(c_byte), c_int]
GetRTLog.restype = c_int

SearchDevice = plcommpro.SearchDevice
SearchDevice.argtypes = [c_char_p, c_char_p, POINTER(c_byte)]
SearchDevice.restype = c_int

ModifyIPAddress = plcommpro.ModifyIPAddress
ModifyIPAddress.argtypes = [c_char_p, c_char_p, c_char_p]
ModifyIPAddress.restype = c_int

PullLastError = plcommpro.PullLastError
PullLastError.restype = c_int

# Global variables
h = None  # Connection handle
rtlog_enabled = False

def connect_device(protocol, ip_address, port, timeout=5000, password=""):
    """
    Connect to the device using the specified parameters.
    :param protocol: Communication protocol ("TCP" or "RS485").
    :param ip_address: IP address of the device (for TCP).
    :param port: Port number for communication (default is 4370 for TCP).
    :param timeout: Connection timeout in milliseconds (default is 5000 ms).
    :param password: Connection password (if required).
    :return: Connection handle if successful, None otherwise.
    """
    connection_params = (
        f"protocol={protocol},"
        f"ipaddress={ip_address},"
        f"port={port},"
        f"timeout={timeout},"
        f"passwd={password}"
    )
    connection_params_bytes = connection_params.encode('utf-8')
    handle = Connect(c_char_p(connection_params_bytes))
    
    if handle:
        print(f"✅ Connected successfully. Handle: {handle}")
        return handle
    else:
        error_code = PullLastError()
        print(f"❌ Failed to connect to the device. Error code: {error_code}")
        return None


def disconnect_device(handle):
    """
    Disconnect from the device.
    :param handle: Connection handle.
    """
    if handle and handle != c_void_p(0):
        Disconnect(handle)
        print("✅ Disconnected from the device.")
    else:
        print("❌ No active connection to disconnect.")


def get_device_param(handle, item_values):
    """
    Retrieve device parameters.
    :param handle: Connection handle.
    :param item_values: Comma-separated list of parameter names.
    :return: Dictionary of parameter values if successful, None otherwise.
    """
    buffer_size = 10 * 1024 * 1024  # 10 MB buffer
    buffer = (c_byte * buffer_size)()
    ret = GetDeviceParam(handle, buffer, buffer_size, item_values.encode('utf-8'))
    
    if ret >= 0:
        raw_data = bytes(buffer).decode('utf-8', errors='ignore').strip('\x00')
        params = {}
        for pair in raw_data.split(','):
            key, value = pair.split('=')
            params[key.strip()] = value.strip()
        return params
    else:
        print(f"❌ Failed to retrieve device parameters. Error code: {ret}")
        return None


def set_device_param(handle, param_string):
    """
    Set device parameters.
    :param handle: Connection handle.
    :param param_string: Comma-separated key-value pairs of parameters.
    :return: True if successful, False otherwise.
    """
    ret = SetDeviceParam(handle, param_string.encode('utf-8'))
    if ret >= 0:
        print("✅ Device parameters set successfully.")
        return True
    else:
        print(f"❌ Failed to set device parameters. Error code: {ret}")
        return False


def control_device(handle, operation_id, param1=0, param2=0, param3=0, param4=0, options=""):
    """
    Control the device (e.g., lock/unlock doors, reboot, etc.).
    :param handle: Connection handle.
    :param operation_id: Operation ID (e.g., 1 for output control, 2 for cancel alarm, etc.).
    :param param1: Parameter 1 (depends on operation).
    :param param2: Parameter 2 (depends on operation).
    :param param3: Parameter 3 (depends on operation).
    :param param4: Parameter 4 (reserved).
    :param options: Additional options (optional).
    :return: True if successful, False otherwise.
    """
    ret = ControlDevice(handle, operation_id, param1, param2, param3, param4, options.encode('utf-8'))
    if ret >= 0:
        print("✅ Device control operation succeeded.")
        return True
    else:
        print(f"❌ Device control operation failed. Error code: {ret}")
        return False


def get_rtlog(handle, buffer_size=256):
    """
    Retrieve real-time logs from the device.
    :param handle: Connection handle.
    :param buffer_size: Size of the buffer to store log data.
    :return: List of log entries if successful, None otherwise.
    """
    buffer = (c_byte * buffer_size)()
    ret = GetRTLog(handle, buffer, buffer_size)
    
    if ret >= 0:
        raw_data = bytes(buffer).decode('utf-8', errors='ignore').strip('\x00')
        logs = raw_data.split(',')
        return logs
    else:
        print(f"❌ Failed to retrieve real-time logs. Error code: {ret}")
        return None


def search_device(comm_type="UDP", address="255.255.255.255"):
    """
    Search for devices in the network.
    :param comm_type: Communication type (e.g., "UDP").
    :param address: Broadcast address (default is "255.255.255.255").
    :return: List of discovered devices if successful, None otherwise.
    """
    buffer_size = 64 * 1024  # 64 KB buffer
    buffer = (c_byte * buffer_size)()
    ret = SearchDevice(comm_type.encode('utf-8'), address.encode('utf-8'), buffer)
    
    if ret >= 0:
        raw_data = bytes(buffer).decode('utf-8', errors='ignore').strip('\x00')
        devices = raw_data.split('\r\n')
        return devices
    else:
        print(f"❌ Failed to search for devices. Error code: {ret}")
        return None


def modify_ip_address(comm_type, address, mac, new_ip):
    """
    Modify the IP address of a device.
    :param comm_type: Communication type (e.g., "UDP").
    :param address: Broadcast address.
    :param mac: MAC address of the device.
    :param new_ip: New IP address to assign.
    :return: True if successful, False otherwise.
    """
    buffer = f"MAC={mac},IPAddress={new_ip}"
    ret = ModifyIPAddress(comm_type.encode('utf-8'), address.encode('utf-8'), buffer.encode('utf-8'))
    if ret >= 0:
        print("✅ IP address modified successfully.")
        return True
    else:
        print(f"❌ Failed to modify IP address. Error code: {ret}")
        return False


# Example usage
if __name__ == "__main__":
    # Connect to the device
    h = connect_device("TCP", "192.168.1.222", 14370, timeout=10000)

    if h:
        # Retrieve device parameters
        params = get_device_param(h, "LockCount,AuxOutCount")
        if params:
            print("Device Parameters:", params)

        # Set device parameters
        set_device_param(h, "DateTime=20231001120000")

        # Control the device (e.g., open door 1)
        control_device(h, operation_id=1, param1=1, param2=1, param3=5)

        # Retrieve real-time logs
        logs = get_rtlog(h)
        if logs:
            print("Real-Time Logs:", logs)

        # Search for devices
        devices = search_device()
        if devices:
            print("Discovered Devices:", devices)

        # Modify IP address of a device
        # modify_ip_address("UDP", "255.255.255.255", "00:11:22:33:44:55", "192.168.1.202")

        # Disconnect from the device
        disconnect_device(h)