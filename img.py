import os
from PIL import Image, ImageDraw, ImageFont

# ตั้งค่าโฟลเดอร์รูปต้นทาง และปลายทาง
input_folder = "input_images"  # โฟลเดอร์ที่มีรูป 1,000 รูป
output_folder = "output_images"  # โฟลเดอร์ที่บันทึกผลลัพธ์

# ตรวจสอบว่ามีโฟลเดอร์ output หรือไม่ ถ้าไม่มีให้สร้าง
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# โหลดฟอนต์ RSU (ต้องมีไฟล์ RSU.ttf ในโฟลเดอร์เดียวกับโค้ด)
try:
    font = ImageFont.truetype("RSU_Regular.ttf", 16)  # ฟอนต์ RSU ขนาด 9px
except IOError:
    print("⚠️ ไม่พบไฟล์ฟอนต์ RSU.ttf กรุณาใส่ไฟล์ฟอนต์ในโฟลเดอร์เดียวกับโค้ด")
    exit()

# วนลูปอ่านไฟล์ภาพทั้งหมดในโฟลเดอร์ input
for filename in os.listdir(input_folder):
    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):  # รองรับไฟล์ .png, .jpg, .jpeg, .bmp
        image_path = os.path.join(input_folder, filename)
        img = Image.open(image_path)

        # สร้างพื้นที่วาดข้อความ
        draw = ImageDraw.Draw(img)

        # ดึงชื่อไฟล์โดยไม่เอาสกุลไฟล์
        file_name_only = os.path.splitext(filename)[0]  # ตัดนามสกุลออก เช่น "image1.jpg" → "image1"

        # ขนาดของรูป
        img_width, img_height = img.size

        # ขนาดของข้อความ
        text_bbox = font.getbbox(file_name_only)  # ใช้ getbbox แทน textsize()
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # ตำแหน่งข้อความ (มุมขวาล่าง)
        x = img_width - text_width - 10  # เว้นขอบ 10 px
        y = img_height - text_height - 10

        # วาดตัวหนังสือสีดำลงบนรูป
        draw.text((x, y), file_name_only, fill="black", font=font)

        # บันทึกรูปภาพใหม่ไปที่โฟลเดอร์ output
        output_path = os.path.join(output_folder, filename)
        img.save(output_path)

print("✅ เสร็จสิ้น! รูปทั้งหมดถูกบันทึกไว้ที่", output_folder)
