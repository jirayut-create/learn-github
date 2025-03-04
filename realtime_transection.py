from functionzk import *
import time

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
        try:
            data = buffer.value.decode('utf-8').strip()
            return data if data else None
        except UnicodeDecodeError:
            return None
    else:
        return None



def fetch_all_transactions(dll, handle):
    """
    ดึงข้อมูลทั้งหมดจากตาราง transaction ก่อนเริ่มดึงแบบเรียลไทม์
    """
    print("📡 Fetching all past transactions...")
    table_name = "transaction"
    
    data = get_device_data(dll, handle, table_name)
    
    if data:
        lines = data.strip().split("\n")
        headers = lines[0].split(",")
        datalist = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split(",")
                # datalist.append(dict(zip(headers, values)))
                
                log = dict(zip(headers, values))
                if log.get("Pin") != "0":  # กรองเฉพาะรายการที่ Pin ไม่เท่ากับ 0
                    datalist.append(log)
        
        # for log in datalist:
        #     # print(f"📍 {log}")
        
        return [tuple(log.items()) for log in datalist]  # เก็บรายการล่าสุดในรูปแบบ tuple
    else:
        print("⚠️ No past transaction data found.")
        return []

def fetch_real_time_transactions(dll, handle, last_transaction):
    """
    ดึงข้อมูลจากตาราง transaction แบบเรียลไทม์ เมื่อมีรายการใหม่
    """
    if not handle:
        print("❌ Invalid device handle. Unable to fetch transactions.")
        return

    table_name = "transaction"
    
    print("📡 Monitoring real-time transaction logs... (Press Ctrl+C to stop)")
    
    try:
        while True:
            data = get_device_data(dll, handle, table_name)

            if data:
                lines = data.strip().split("\n")
                headers = lines[0].split(",")  # หัวข้อของข้อมูล
                datalist = []

                for line in lines[1:]:
                    if line.strip():
                        values = line.split(",")
                        # datalist.append(dict(zip(headers, values)))
                        
                        log = dict(zip(headers, values))
                        datalist.append(log)
                        # if log.get("Pin") != "0":  # กรองเฉพาะรายการที่ Pin ไม่เท่ากับ 0
                        #     datalist.append(log)

                # แปลงข้อมูลใหม่เป็น tuple เพื่อเปรียบเทียบกับ last_transaction
                datalist_tuples = [tuple(log.items()) for log in datalist]
                new_data = [log for log in datalist if tuple(log.items()) not in last_transaction]
                
                for log in new_data:
                    print(f"📍 {log}")  # แสดงข้อมูลแต่ละรายการ

                last_transaction = datalist_tuples  # อัปเดตข้อมูลล่าสุดที่ถูกดึงมา

            time.sleep(0.5)  # รอ 0.5 วินาที แล้วดึงข้อมูลใหม่
    except KeyboardInterrupt:
        print("⏹️ Stopping real-time monitoring.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    dll_path = r"C:\\learn-github\\Pull_SDK\\plcommpro.dll"
    dll = load_dll(dll_path)

    if not dll:
        print("❌ Failed to load DLL. Exiting...")
        return

    handle = connect_device(dll, "192.168.1.222", 14370)

    if handle:
        try:
            last_transaction = fetch_all_transactions(dll, handle)  # ดึงข้อมูลทั้งหมดก่อนและเก็บรายการล่าสุด
            fetch_real_time_transactions(dll, handle, last_transaction)  # ดึงข้อมูลแบบ Real-time
        finally:
            disconnect_device(dll, handle)  # ตัดการเชื่อมต่ออุปกรณ์
            print("🔌 Device disconnected.")

if __name__ == "__main__":
    main()
