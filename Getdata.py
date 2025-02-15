from functionzk import *

def main() :
    dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"
    dll = load_dll(dll_path)
    handle = connect_device(dll,"192.168.1.222",14370)
    open_time=5
    door_id = 1
    
     # ลองดึงข้อมูลผู้ใช้จากตารางต่าง ๆ
    user_tables_to_try = ["user"]
    fetch_data_from_tables(dll, handle, user_tables_to_try)
    
    # ลองดึงข้อมูลผู้ใช้จากตารางต่าง ๆ extuser
    extuser_tables_to_try = ["extuser"]
    fetch_data_from_tables(dll, handle, extuser_tables_to_try)

    # ลองดึงข้อมูลการอนุญาตจากตารางต่าง ๆ mulcarduser
    mulcarduser_tables_to_try = ["mulcarduser"]
    fetch_data_from_tables(dll, handle, mulcarduser_tables_to_try)
    
    # ลองดึงข้อมูลการอนุญาตจากตารางต่าง ๆ
    auth_tables_to_try = ["userauthorize"]
    fetch_data_from_tables(dll, handle, auth_tables_to_try)
    

    # ลองดึงข้อมูลจากตารางอื่น ๆ
    other_tables_to_try = ["templatev10"]
    fetch_data_from_tables(dll, handle, other_tables_to_try)

if __name__ == "__main__":
    main()
