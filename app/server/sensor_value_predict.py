from datetime import datetime
import pandas as pd
import requests
from app.server.comfort_index_module import preprocess, predict, load_model, load_iso_model

sensor_cache = {}
required_features = ['temperature', 'humidity', 'co2']

area_map = {
    "보드": 31.59,
    "왼쪽 뒤": 109.21,
    "안쪽벽 중앙": 25.13,
    "8인 책상": 64.65
}

def update_sensor_data(location, sensor_type, value):
    if location not in sensor_cache:
        sensor_cache[location] = {}
    sensor_cache[location][sensor_type] = value
    sensor_cache[location]['timestamp'] = datetime.now()

    if is_ready(sensor_cache[location]):
        df = build_dataframe(location, sensor_cache[location])
        model = load_model()
        iso_model = load_iso_model()
        pred_di = predict(model, df, iso_model=iso_model)[0]

        t = df['temperature'].iloc[0]
        h = df['humidity'].iloc[0]
        c = df['co2'].iloc[0]
        area = area_map.get(location, 50)

        ecdi = compute_ecdi(pred_di, c, area)
        label = ecdi_to_label(ecdi)

        print(f"📢 최종 ECDI: {ecdi:.2f} → 상태: {label}")
        send_prediction_result(location, ecdi)
        sensor_cache[location].clear()

def environment_score(temp, humi, co2, occ_density=None):
    score = 0
    if temp < 19:
        score -= 1   # -2 → -1 (완화)
    elif temp > 28:
        score -= 1

    if humi < 30 or humi > 70:
        score -= 1

    if co2 > 1200:   # 1000 → 1200 정도로 상향
        score -= 1

    if occ_density and occ_density > 0.4:  # 0.3 → 0.4
        score -= 1

    return score


def ecdi_to_label(ecdi):
    if ecdi < 63:
        return "❄️ 매우 추움"
    elif ecdi < 67:
        return "🥶 추움"
    elif ecdi < 70:
        return "😊 쾌적"
    elif ecdi < 73:
        return "🙂 약간 더움"
    elif ecdi < 76:
        return "😓 불쾌"
    elif ecdi < 80:
        return "🥵 매우 불쾌"
    else:
        return "🔥 극심한 불쾌"


    
def compute_ecdi(di, co2, area):
    co2_density = co2 / area
    ecdi = di + 0.01 * co2_density  # 필요시 계수 튜닝
    return round(ecdi, 2)



# 예측 조건 검사
def is_ready(data):
    return all(k in data for k in required_features)

# 모델 입력을 위한 row 생성
def build_dataframe(location, values):
    row = {
        'location': location,
        'temperature': values['temperature'],
        'humidity': values['humidity'],
        'co2': values['co2']
    }
    df = pd.DataFrame([row])
    return preprocess(df)

import requests

# 예측 결과를 외부(Spring 등) 서버로 전송
SPRING_RULE_ENGINE_URL = "http://localhost:8080/comfort/result"  # 실제 포트로 수정

# def send_prediction_result(location, value):
#     payload = {
#         "location": location,
#         "comfortIndex": float(round(value, 4)),
#         "timestamp": datetime.now().isoformat()
#     }
#     try:
#         res = requests.post(SPRING_RULE_ENGINE_URL, json=payload, timeout=3)
#         print(f"✅ 쾌적지수 전송 완료 | 응답코드: {res.status_code}")
#     except Exception as e:
#         print(f"❌ 전송 실패: {e}")
def send_prediction_result(location, value):
    print(f"📤 [TEST] 쾌적지수 전송: {location} → {round(value, 4)}")
