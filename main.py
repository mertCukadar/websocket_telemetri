import serial
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Seri port ayarları (Bağlantı noktanı kontrol et!)
SERIAL_PORT = "/dev/ttyUSB0"  # veya "/dev/ttyACM0"
BAUDRATE = 9600

# FastAPI başlat
app = FastAPI()

@app.get("/")
def read_root():
    return{"gello" : "alaz"}


# CORS izinleri (Next.js gibi farklı bir porttan erişim için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seri bağlantıyı aç
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

def parse_data(line: str):
    """Gelen sensör verisini ayrıştırır"""
    if "Acc" in line:
        parts = line.replace("gelen_veri:Acc: ", "").split(", ")
        return {"accelerometer": {"x": parts[0], "y": parts[1], "z": parts[2]}}
    elif "Metan" in line:
        value = line.replace("gelen_veri:Metan Unit: ", "")
        return {"metan": value}
    elif "Temperature" in line:
        value = line.replace("gelen_veri:Temperature: ", "").replace(" C", "")
        return {"temperature": value}
    return {}

@app.get("/sensor-data")
def get_sensor_data():
    """Sensör verisini okur ve JSON formatında döndürür"""
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            return parse_data(line)
        return {"error": "No Data"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
