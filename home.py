from module.conn import *
from module.openGate import *
from module.Getedata import *
from module.adduser import *
from module.Deletedata import *


if __name__ == "__main__":
    try:
        dll = load_dll(dll_path)
        handle = connect_device(dll, "192.168.1.222", 14370)
        print(f"✅ Connected successfully! Handle: {handle}")
        # control_door(dll, handle, door_id=3, open_time=5)
        # ลองดึงข้อมูลผู้ใช้จากตารางต่าง ๆ
        user_tables_to_try = ["user"]
        # fetch_data_from_tables(dll, handle, user_tables_to_try)
        
        delete_user_by_pin(dll, handle, 16)
        fetch_data_from_tables(dll, handle, user_tables_to_try)

        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'handle' in locals():
            disconnect_device(dll, handle)
            print("🔌 Disconnected.")
            