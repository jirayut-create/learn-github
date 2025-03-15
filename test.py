from ctypes import *
import os
from module.conn import *


def add_user(dll, handle, user_data, mulcarduser_data, userauthorize_data):
    # เพิ่มข้อมูลลงในตาราง user
    result = dll.SetDeviceData(handle, b"user", user_data.encode('utf-8'), b"")
    if result == 0:
        print("✅ เพิ่มข้อมูล user สำเร็จ!")
    else:
        print(f"❌ ล้มเหลว! รหัสข้อผิดพลาด: {result}")

    # เพิ่มข้อมูลลงในตาราง mulcarduser
    result = dll.SetDeviceData(handle, b"mulcarduser", mulcarduser_data.encode('utf-8'), b"")
    if result == 0:
        print("✅ เพิ่มข้อมูล mulcarduser สำเร็จ!")
    else:
        print(f"❌ ล้มเหลว! รหัสข้อผิดพลาด: {result}")
    
    # เพิ่มข้อมูลลงในตาราง userauthorize
    result = dll.SetDeviceData(handle, b"userauthorize", userauthorize_data.encode('utf-8'), b"")
    if result == 0:
        print("✅ เพิ่มข้อมูล userauthorize สำเร็จ!")
    else:
        print(f"❌ ล้มเหลว! รหัสข้อผิดพลาด: {result}")


if __name__ == "__main__":
    try:
        dll = load_dll(dll_path)
        handle = connect_device(dll, "192.168.1.222", 14370)
        print(f"✅ Connected successfully! Handle: {handle}")      
        
        # ข้อมูลที่จะเพิ่ม
        user_data = (
            "CardNo=44444\t"
            "Pin=17\t"
            "Password=\t"
            "Group=0\t"
            "StartTime=0\t"
            "EndTime=0\t"
            "Name=sdsd\t"
            "SuperAuthorize=0\t"
            "Disable=0"
        )

        mulcarduser_data = "Pin=17\tCardNo=4444\tLossCardFlag=0"
        
        userauthorize_data = "Pin=17\tAuthorizeTimezoneId=1\tAuthorizeDoorId=15"

        # เพิ่มข้อมูลผู้ใช้
        add_user(dll, handle, user_data, mulcarduser_data, userauthorize_data)

     
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'handle' in locals():
            # disconnect_device(dll, handle)
            print("🔌 Disconnected.")