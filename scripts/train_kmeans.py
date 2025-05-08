import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib
import os
os.chdir(os.path.dirname(__file__) or '.')

# 데이터 로드
df = pd.read_csv('../notebooks/labeled_sensor_data.csv')
X  = df[['co2','temperature','humidity','co2_per_area']]

# 파이프라인 정의
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('kmeans',  KMeans(n_clusters=3, random_state=42))
])
pipe.fit(X)

# 저장
joblib.dump(pipe, 'models/kmeans_pipeline.pkl')
print("✅ 모델 저장 완료!")
