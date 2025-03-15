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





