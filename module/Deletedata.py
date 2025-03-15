def delete_data(dll, handle, table_name):
    """
    ลบข้อมูลทั้งหมดในตาราง transaction
    """
    # table_name = "transaction"
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
        


def delete_user_by_pin(dll, handle, pin):
        # เงื่อนไขการลบข้อมูล
        condition = f"Pin={pin}"
        
        # ลบข้อมูลจากตาราง userauthorize
        result = dll.DeleteDeviceData(handle, b"userauthorize", condition.encode('utf-8'), b"")
        if result == 0:
            print(f"✅ ลบ userauthorize PIN {pin} สำเร็จ!")
        else:
            print(f"❌ ล้มเหลว! รหัสข้อผิดพลาด: {result}")
            
            
        # ลบข้อมูลจากตาราง mulcarduser
        result = dll.DeleteDeviceData(handle, b"mulcarduser", condition.encode('utf-8'), b"")
        if result == 0:
            print(f"✅ ลบ mulcarduser PIN {pin} สำเร็จ!")
        else:
            print(f"❌ ล้มเหลว! รหัสข้อผิดพลาด: {result}")
        
        # ลบข้อมูลจากตาราง user
        result = dll.DeleteDeviceData(handle, b"user", condition.encode('utf-8'), b"")
        if result == 0:
            print(f"✅ ลบผู้ใช้ PIN {pin} สำเร็จ!")
        else:
            print(f"❌ ล้มเหลว! รหัสข้อผิดพลาด: {result}")