import serial
import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Arduino'nun bağlı olduğu seri portu (Cihazına göre değişebilir)
SERIAL_PORT = "/dev/ttyUSB0"  # veya "/dev/ttyACM0"
BAUDRATE = 9600

app = FastAPI()

# CORS izinleri (Next.js farklı bir portta çalışabilir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket istemcilerini saklamak için liste
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # 1 saniye aralıklarla veri gönder
    except:
        clients.remove(websocket)

async def read_serial():
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            data = parse_data(line)
            await broadcast(data)
        await asyncio.sleep(0.1)

def parse_data(line):
    if "Acc" in line:
        parts = line.replace("gelen_veri:Acc: ", "").split(", ")
        return {"type": "accelerometer", "x": parts[0], "y": parts[1], "z": parts[2]}
    elif "Metan" in line:
        value = line.replace("gelen_veri:Metan Unit: ", "")
        return {"type": "metan", "value": value}
    elif "Temperature" in line:
        value = line.replace("gelen_veri:Temperature: ", "").replace(" C", "")
        return {"type": "temperature", "value": value}
    return {}

async def broadcast(data):
    if clients:
        for client in clients:
            await client.send_text(json.dumps(data))

# Seri haberleşme okuma işlemini başlat
loop = asyncio.get_event_loop()
loop.create_task(read_serial())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
