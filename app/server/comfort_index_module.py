import joblib
import numpy as np
import pandas as pd
import os
os.chdir(os.path.dirname(__file__) or '.')

pipeline = joblib.load('../../scripts/models/kmeans_pipeline.pkl')

_cluster_map = {0:'춥고 건조',1:'덥고 습함',2:'최적 쾌적'}
_area_map    = {
    "보드":31.59, "왼쪽 뒤":109.21,
    "안쪽벽 중앙":25.13, "8인 책상":64.65
}

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    loc = df.loc[0,'location']
    if loc not in _area_map:
        raise ValueError(f"Unknown location: {loc}")
    df = df.copy()
    df['area'] = _area_map[loc]
    df['co2_per_area'] = df['co2'] / df['area']
    return df[['co2','temperature','humidity','co2_per_area']]

def predict_pipeline(df: pd.DataFrame) -> str:
    X = preprocess(df).values
    idx = pipeline.predict(X)[0]
    return _cluster_map[idx]