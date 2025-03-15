from ctypes import *
import os

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