# fast_server.py

from fastapi import FastAPI
from pydantic import BaseModel
from app.server.sensor_value_predict import update_sensor_data, sensor_cache

app = FastAPI()


class SensorPayload(BaseModel):
    location:    str
    sensor_type: str
    value:       float

@app.post("/sensor")
def receive_sensor_data(payload: SensorPayload):
    result = update_sensor_data(
        payload.location,
        payload.sensor_type,
        payload.value
    )
    return result
