# debug_kmeans.py

import joblib
import numpy as np
from sklearn.metrics import pairwise_distances

# 1) 파이프라인 로드
pipe = joblib.load('scripts/models/kmeans_pipeline.pkl')
scaler = pipe.named_steps['scaler']
km     = pipe.named_steps['kmeans']

# 2) 스케일 전센터 복원
centers_scaled = km.cluster_centers_
centers_orig   = scaler.inverse_transform(centers_scaled)
print("=== 스케일 전 클러스터 중심 ===")
for i, c in enumerate(centers_orig):
    print(f"클러스터 {i} 중심 (co2, temp, humi, co2pa): {c}")

# 3) 테스트 입력
co2, temp, humi, area = 800.0, 23.0, 40.0, 31.59
co2pa = co2 / area
x_raw = np.array([[co2, temp, humi, co2pa]])
x_scaled = scaler.transform(x_raw)

# 4) 거리 계산
dists = pairwise_distances(x_scaled, centers_scaled, metric='euclidean')[0]
print("\n=== 입력과 각 클러스터 중심 간 거리 ===")
for i, d in enumerate(dists):
    print(f"클러스터 {i} 거리: {d:.4f}")

# 5) 현재 매핑 확인
mapping = {0:'춥고 건조', 1:'덥고 습함', 2:'최적 쾌적'}
print("\n현재 매핑:", mapping)
print("예측 라벨:", mapping[pipe.predict(x_raw)[0]])
