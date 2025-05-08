from datetime import datetime
import requests
import pandas as pd
from app.server.comfort_index_module import preprocess, predict_pipeline

RULE_ENGINE_URL = "http://localhost:10263/api/v1/comfort"

sensor_cache     = {}
required_fields = ['temperature','humidity','co2']

def is_ready(data):
    return all(f in data for f in required_fields)

def build_dataframe(location, data):
    return pd.DataFrame([{
        'location': location,
        'temperature': data['temperature'],
        'humidity':    data['humidity'],
        'co2':         data['co2']
    }])

def update_sensor_data(location, sensor_type, value):
    # 1) 캐시에 저장
    cache = sensor_cache.setdefault(location, {})
    cache[sensor_type] = value
    cache['timestamp']   = datetime.now()

    # 2) 모든 필드 모이면 예측
    if is_ready(cache):
        df_raw = build_dataframe(location, cache)
        try:
            label = predict_pipeline(df_raw)
        except ValueError as e:
            return {'error': str(e)}

        co2 = cache['co2']
        co2_status = 'CO2 주의' if co2 >= 1000 else 'CO2 양호'
        result = {
            'location':       location,
            'temperature':    cache['temperature'],
            'humidity':       cache['humidity'],
            'comfort_index':  label,
            'co2':            co2,
            'co2_comment':     co2_status
        }

        try:
            resp = requests.post(RULE_ENGINE_URL, json=result, timeout=5)
            resp.raise_for_status()
            print(f"✅ 룰엔진 전송 성공({resp.status_code}): {result}")
        except Exception as e:
            print(f"❌ 룰엔진 전송 실패: {e} | payload={result}")

        # 4) 캐시 초기화
        cache.clear()

        return result
    else:
        # 아직 모자란 필드 알려주기
        missing = [f for f in required_fields if f not in cache]
        return {'status':'waiting_for_data','missing':missing}