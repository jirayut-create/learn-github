from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def receive_data(request: Request):
    data = await request.json()
    print(f"📍 New Event: {data}")
    return {"status": "success"}

