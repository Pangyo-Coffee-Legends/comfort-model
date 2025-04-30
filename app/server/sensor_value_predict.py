from datetime import datetime
import pandas as pd
import requests
from app.server.comfort_index_module import preprocess, predict, load_model, load_iso_model

sensor_cache = {}
required_features = ['temperature', 'humidity', 'co2']

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

        # 🌡 후처리 보정 적용 (쾌적도 라벨 붙이기)
        t = df['temperature'].iloc[0]
        h = df['humidity'].iloc[0]
        c = df['co2'].iloc[0]
        final_di, comfort_label = classify_environment(pred_di, t, h, c)


        print(f"📢 최종 DI: {final_di:.2f} → 상태: {comfort_label}")
        send_prediction_result(location, final_di)
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


def di_to_label(di):
    if di < 65:
        return "😊 쾌적"
    elif di < 70:
        return "🙂 보통"
    elif di < 75:
        return "😓 약간 더움"
    elif di < 80:
        return "🥵 불쾌"
    else:
        return "🔥 매우 불쾌"

def classify_environment(di, temp, humi, co2, occ_density=None):
    base_label = di_to_label(di)
    env_score = environment_score(temp, humi, co2, occ_density)

    if env_score <= -3:
        return di, "❄️ 매우 불쾌 (환경 악화)"
    elif env_score == -2:
        return di, "🥶 불쾌 요소 있음"
    elif env_score == -1:
        return di, f"{base_label} + 경미한 불쾌"
    else:
        return di, base_label



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
