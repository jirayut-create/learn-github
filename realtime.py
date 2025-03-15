
from ctypes import *
import os
import time
import threading
from module.conn import *
from module.Deletedata import *
from module.Reltime_mornitor import *


def main():
    dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"
    dll = load_dll(dll_path)
    handle = connect_device(dll, "192.168.1.222", 14370)
    table_name = "transaction"
    if not dll:
        return

    try:
        # ลบข้อมูลในตาราง transaction
        delete_data(dll, handle, table_name)
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