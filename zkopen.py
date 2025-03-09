from ctypes import cdll, c_char_p, c_long, c_void_p
import os

# ระบุพาธของไฟล์ plcommpro.dll
dll_path = r"C:\dev-zkaccess\Pull_SDK\plcommpro.dll"

# ตรวจสอบว่าไฟล์ DLL มีอยู่หรือไม่
if not os.path.exists(dll_path):
    print(f"❌ Error: File not found - {dll_path}")
else:
    try:
        # โหลด DLL
        zkemkeeper = cdll.LoadLibrary(dll_path)

        # กำหนดค่าการเชื่อมต่อ
        parameters = "protocol=TCP,ipaddress=192.168.1.222,port=14370,timeout=5000,passwd="
        
        # ตั้งค่าประเภทของ Connect()
        zkemkeeper.Connect.argtypes = [c_char_p]
        zkemkeeper.Connect.restype = c_void_p  # คืนค่าเป็น pointer
        
        # เชื่อมต่อกับอุปกรณ์
        connection_handle = zkemkeeper.Connect(parameters.encode('utf-8'))

        # ตรวจสอบค่า handle
        if not connection_handle or connection_handle == 0:
            print("❌ Connection handle is invalid!")
            exit()
        else:
            print(f"✅ เชื่อมต่อสำเร็จ! Connection handle: {connection_handle}")

            # ตั้งค่าพารามิเตอร์ของ ControlDevice()
            zkemkeeper.ControlDevice.argtypes = [c_void_p, c_long, c_long, c_long, c_long, c_long, c_char_p]
            zkemkeeper.ControlDevice.restype = c_long  # คืนค่าเป็น int
            
            # คำสั่งเปิดประตูที่ 1 เป็นเวลา 5 วินาที
            door_id = 2
            operation_id = 1  # 1 = ควบคุมการล็อค
            output_type = 1  # 1 = ล็อค
            open_time = 2  # เปิดเป็นเวลา 5 วินาที
            reserved = 0  # ไม่ใช้
            options = c_char_p(b"")  # แก้ไขตรงนี้ ใช้ string ว่างแทน None
            
            # พิมพ์ค่าพารามิเตอร์ก่อนเรียกใช้งาน
            print(f"🔍 Params: OperationID={operation_id}, DoorID={door_id}, OutputType={output_type}, OpenTime={open_time}")

            # เรียกใช้คำสั่งเปิดประตู
            result = zkemkeeper.ControlDevice(connection_handle, operation_id, door_id, output_type, open_time, reserved, options)
            
            if result >= 0:
                print(f"🚪✅ เปิดประตู {door_id} สำเร็จ!")
            else:
                print(f"🚪❌ เปิดประตู {door_id} ล้มเหลว! Error Code: {result}")

            # ปิดการเชื่อมต่อ
            # zkemkeeper.Disconnect.argtypes = [c_void_p]
            # zkemkeeper.Disconnect(connection_handle)
             # เชื่อมต่อกับอุปกรณ์
            connection_handle = zkemkeeper.Connect(parameters.encode('utf-8'))

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
