from fastapi import FastAPI
from pydantic import BaseModel
from app.server.sensor_value_predict import update_sensor_data
 
app = FastAPI()

class SensorPayload(BaseModel):
    location: str
    sensor_type: str
    value: float

# @app.post("/sensor")
# def receive_sensor_data(payload: SensorPayload):
#     update_sensor_data(payload.location, payload.sensor_type, payload.value)
#     return {"status": "received"}

@app.post("/sensor")
def receive_sensor_data(payload: SensorPayload):
    update_sensor_data(payload.location, payload.sensor_type, payload.value)
    from app.server.sensor_value_predict import sensor_cache
    if payload.location in sensor_cache:
        last = sensor_cache[payload.location]
        if 'comfort_index' in last:
            return {"comfort_index": last['comfort_index']}
    return {"status": "received"}
