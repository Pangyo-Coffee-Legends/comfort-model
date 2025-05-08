import joblib
import numpy as np

pipe = joblib.load('models/kmeans_pipeline.pkl')
mapping = {0:'춥고 건조',1:'덥고 습함',2:'최적 쾌적'}

def predict_state(co2, temp, humi, area):
    co2pa = co2 / area
    raw   = np.array([[co2, temp, humi, co2pa]])
    idx   = pipe.predict(raw)[0]
    return mapping[idx]
