from sklearn.preprocessing import RobustScaler
import pandas as pd
import joblib

# 불쾌지수 공식
def compute_discomfort_index(t, rh):
    return 0.81 * t + 0.01 * rh * (0.99 * t - 14.3) + 46.3

# 전처리 함수
def preprocess(raw_df):
    # 👉 결측치 제거 또는 단순 평균 보간 (센서 데이터는 결측 거의 없음 가정)
    raw_df = raw_df.fillna(raw_df.mean(numeric_only=True))

    # 스케일링 (학습에 사용한 RobustScaler 그대로 사용)
    scaler = joblib.load("app/server/scaler.pkl")
    raw_df[['temperature', 'humidity', 'co2']] = scaler.transform(raw_df[['temperature', 'humidity', 'co2']])
    return raw_df

def load_model(path='app/server/model.pkl'):
    return joblib.load(path)

def load_iso_model(path='app/server/iso_model.pkl'):
    return joblib.load(path)

# 예측 수행
def predict(model, df, iso_model=None):
    features = ['temperature', 'humidity', 'co2']
    X = df[features]
    pred = model.predict(X)
    if iso_model:
        pred = iso_model.predict(pred)
    return pred

# 모델 저장 (사용 안 해도 유지)
def save_model(model, path='app/server/model.pkl'):
    joblib.dump(model, path)
