from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from datetime import datetime
import os
from requests.auth import HTTPDigestAuth

app = Flask(__name__)
app.secret_key = 'secret_key_for_flask_flash'

# ตั้งค่า IP Camera
CAMERA_IP = "192.168.1.22"          # แก้ไขให้ตรงกับกล้อง
CAMERA_USER = "admin"
CAMERA_PASS = "Admin12345"

# พาธที่ใช้บันทึกรูป
SAVE_PATH = "captured_images"

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        # URL เรียกภาพ snapshot ของ Hikvision (stream 1)
        snapshot_url = f"http://{CAMERA_IP}/ISAPI/Streaming/channels/101/picture"

        # ส่ง request ไปยังกล้อง (ใช้ Digest Auth)
        response = requests.get(snapshot_url, auth=HTTPDigestAuth(CAMERA_USER, CAMERA_PASS), stream=True)

        if response.status_code == 200:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
            filepath = os.path.join(SAVE_PATH, filename)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            flash(f"📸 บันทึกรูปภาพสำเร็จ: {filename}", "success")
        else:
            flash(f"❌ ไม่สามารถดึงภาพจากกล้องได้ (HTTP {response.status_code})", "danger")

    except Exception as e:
        flash(f"⚠️ เกิดข้อผิดพลาด: {str(e)}", "danger")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
