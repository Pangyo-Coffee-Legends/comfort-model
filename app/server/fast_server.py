# fast_server.py

from fastapi import FastAPI
from pydantic import BaseModel
from app.server.sensor_value_predict import update_sensor_data, sensor_cache
import logging


logger = logging.getLogger("uvicorn.access")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger.setLevel(logging.INFO)

app_logger = logging.getLogger("comfort-model")
app_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
app_logger.addHandler(handler)
app = FastAPI()


class SensorPayload(BaseModel):
    location:    str
    sensor_type: str
    value:       float

@app.post("/api/v1/sensor")
def receive_sensor_data(payload: SensorPayload):
    app_logger.info(f"센서 데이터 수신: {payload.location} - {payload.sensor_type} - {payload.value}")
    result = update_sensor_data(
        payload.location,
        payload.sensor_type,
        payload.value
    )
    return result

@app.get("/health")
def health():
    return {"status": "ok"}
