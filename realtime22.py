# การดึงข้อมูลเรีบลไทม์ยังช้าอยู่


from ctypes import *
import os
import time
import threading

def load_dll(dll_path):
    if not os.path.exists(dll_path):
        print(f"\u274c File not found: {dll_path}")
        return None
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

def fetch_new_data(dll, handle, table_name, fetched_data):
    """
    ดึงข้อมูลใหม่และกรองข้อมูลที่เคยดึงมาแล้ว
    """
    data = get_device_data(dll, handle, table_name)
    if data.startswith("\u274c"):
        if "Error! Code: -2" in data:
            print("\u26A0 Connection lost. Attempting to reconnect...")
            return None, fetched_data  # ส่งสัญญาณให้ทำการเชื่อมต่อใหม่
        else:
            print(data)  # แสดงข้อผิดพลาดอื่น ๆ
            return None, fetched_data

    # แยกข้อมูลเป็นบรรทัด (ถ้าข้อมูลเป็น CSV หรือแบ่งด้วย newline)
    new_data_lines = data.splitlines()
    new_unique_data = []

    for line in new_data_lines:
        if line not in fetched_data:  # ตรวจสอบว่าข้อมูลนี้เคยดึงมาแล้วหรือไม่
            new_unique_data.append(line)
            fetched_data.add(line)  # เพิ่มข้อมูลใหม่ลงในเซต

    if new_unique_data:
        return "\n".join(new_unique_data), fetched_data
    else:
        return "\u26A0 No new data found.", fetched_data

def disconnect_device(dll, handle):
    dll.Disconnect.argtypes = [c_void_p]
    dll.Disconnect(handle)

def realtime_data_fetch(dll, ip, port, table_name, interval=5):
    """
    ดึงข้อมูลแบบเรียลไทม์
    """
    handle = None
    fetched_data = set()  # ใช้เซตเพื่อเก็บข้อมูลที่เคยดึงมาแล้ว

    while True:
        try:
            if not handle:
                handle = connect_device(dll, ip, port)
                print("\u2705 Connected to device.")

            # ดึงข้อมูลใหม่และกรองข้อมูลที่เคยดึงมาแล้ว
            data, fetched_data = fetch_new_data(dll, handle, table_name, fetched_data)
            if data is None:
                if handle:
                    disconnect_device(dll, handle)
                    handle = None
                continue

            if data != "\u26A0 No new data found.":
                print(data)

        except Exception as e:
            print(f"\u274c Error: {str(e)}")
            if handle:
                disconnect_device(dll, handle)
                handle = None
            time.sleep(interval)  # รอสักครู่ก่อนลองใหม่
            continue

        time.sleep(interval)

def main():
    dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"
    dll = load_dll(dll_path)
    handle = connect_device(dll, "192.168.1.222", 14370)
    if not dll:
        return

    try:
        # สร้างเธรดสำหรับดึงข้อมูลแบบเรียลไทม์
        realtime_thread = threading.Thread(
            target=realtime_data_fetch,
            args=(dll, "192.168.1.222", 14370, "transaction")
        )
        realtime_thread.daemon = True
        realtime_thread.start()

        # รอให้ผู้ใช้กด Ctrl+C เพื่อหยุดโปรแกรม
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\u26A0 Program interrupted by user.")
    finally:
        if 'dll' in locals():
            disconnect_device(dll, handle)
        print("\u2705 Disconnected from device.")

if __name__ == "__main__":
    main()