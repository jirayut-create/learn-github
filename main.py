from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import json

app = FastAPI()

# ตั้งค่า Jinja2
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class IPRequest(BaseModel):
    ip: str
    door: str
    
class DoorRequest(BaseModel):
    door: str  # ใช้สำหรับ API เปิดประตูโดยไม่เช็ค IP

# หน้าเว็บหลัก
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register/") 
async def home(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
# API เช็ค IP ผ่าน OpenDoor.py
@app.post("/check_ip/")
async def check_ip(data: IPRequest):
    try:
        result = subprocess.run(
            ["python", "OpenDoor.py", data.ip,data.door], capture_output=True, text=True
        )

        response_text = result.stdout.strip()
        
        # ✅ ตรวจสอบว่า output เป็น JSON จริงหรือไม่
        try:
            response_json = json.loads(response_text)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"❌ รูปแบบข้อมูลผิดพลาด: {response_text}")

        return response_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API เช็ค IP ผ่าน OpenDoor.py
@app.post("/open_door/")
async def open_door(data: DoorRequest):
    try:
        result = subprocess.run(
            ["python", "open.py", data.door], capture_output=True, text=True
        )

        response_text = result.stdout.strip()
        
        # ✅ ตรวจสอบว่า output เป็น JSON จริงหรือไม่
        try:
            response_json = json.loads(response_text)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"❌ รูปแบบข้อมูลผิดพลาด: {response_text}")

        return response_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))