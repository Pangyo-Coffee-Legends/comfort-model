from datetime import datetime
import pandas as pd
from app.server.comfort_index_module import preprocess, predict_pipeline

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
            # 위치 매핑 오류 등
            return {'error': str(e)}

        co2 = cache['co2']
        co2_status = 'CO2 주의' if co2 >= 1000 else 'CO2 양호'
        result = {
            'location':       location,
            'temperature':    cache['temperature'],
            'humidity':       cache['humidity'],
            'co2':            co2,
            'comfort_index':  label,
            'co2_status':     co2_status
        }

        # 전송 및 캐시 초기화
        print(f"📤 예측 전송: {result}")
        cache.clear()
        return result
    else:
        # 아직 모자란 필드 알려주기
        missing = [f for f in required_fields if f not in cache]
        return {'status':'waiting_for_data','missing':missing}