from ctypes import *
import time
from module.conn import *

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
