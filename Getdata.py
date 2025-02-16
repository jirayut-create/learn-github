from functionzk import *

def fetch_datas(dll, handle, tables):
    """
    ดึงข้อมูลจากตารางต่าง ๆ
    """
    for table in tables:
        print(f"\nTrying to fetch data from table: {table}")
        try:
            data = get_device_data(dll, handle, table)
            
            # ตรวจสอบว่าข้อมูลไม่เป็น None และไม่ว่างเปล่า
            if data is None or data.strip() == "":
                print(f"No data found in table: {table}")
                continue
            
            print(f"[Data from {table}]\n", data)
            
            # ตรวจสอบว่าข้อมูลไม่เริ่มต้นด้วยสัญลักษณ์ ❌ (\u274c)
            if data.startswith("\u274c"):
                print("Data retrieval failed with error symbol ❌")
                continue
            
            # แปลงข้อมูลเป็น List ของ Dictionary (ถ้าจำเป็น)
            lines = data.split("\n")
            headers = lines[0].split(",")
            datalist = []
            
            for line in lines[1:]:
                if line.strip():  # ตรวจสอบว่าไม่ใช่บรรทัดว่าง
                    values = line.split(",")
                    datalist.append(dict(zip(headers, values)))
            
            # แสดงผลข้อมูล ทั้งหมด
            # for record in datalist:
            #     print(record)
            
            # หากต้องการกรองข้อมูล เช่น ดึงเฉพาะผู้ใช้ที่มี
            filtered_data = [record for record in datalist if record["Pin"] == "10005"]
            print(filtered_data)
            
            break  # หยุดการทำงานเมื่อดึงข้อมูลสำเร็จ
        except Exception as e:
            print(f"Error fetching data from table {table}: {e}")
            continue

def main() :
    dll_path = r"C:\learn-github\Pull_SDK\plcommpro.dll"
    dll = load_dll(dll_path)
    handle = connect_device(dll,"192.168.1.222",14370)
    open_time=5
    door_id = 1
    
    
     # ลองดึงข้อมูลผู้ใช้จากตารางต่าง ๆ
    user_tables_to_try = ["transaction"]
    fetch_datas(dll, handle, user_tables_to_try)

    
    # # ลองดึงข้อมูลผู้ใช้จากตารางต่าง ๆ extuser
    # extuser_tables_to_try = ["extuser"]
    # fetch_data_from_tables(dll, handle, extuser_tables_to_try)

    # # ลองดึงข้อมูลการอนุญาตจากตารางต่าง ๆ mulcarduser
    # mulcarduser_tables_to_try = ["mulcarduser"]
    # fetch_data_from_tables(dll, handle, mulcarduser_tables_to_try)
    
    # # ลองดึงข้อมูลการอนุญาตจากตารางต่าง ๆ
    # auth_tables_to_try = ["userauthorize"]
    # fetch_data_from_tables(dll, handle, auth_tables_to_try)
    

    # # ลองดึงข้อมูลจากตารางอื่น ๆ
    # other_tables_to_try = ["templatev10"]
    # fetch_data_from_tables(dll, handle, other_tables_to_try)

if __name__ == "__main__":
    main()
