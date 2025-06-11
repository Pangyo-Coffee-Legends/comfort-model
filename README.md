# Comfort Model

실내 환경 센서 데이터로부터 쾌적 지수를 예측하는 FastAPI 기반 마이크로서비스입니다. 
CO2, 온도, 습도 값을 활용하여 K-means 클러스터링 모델을 통해 상태를 분류하고, 결과를 룰 엔진에 전달합니다.

## 구조

```
app/                    서버 코드
  server/
    fast_server.py      FastAPI 엔드포인트 정의
    sensor_value_predict.py   센서 데이터 수신 및 예측 로직
    comfort_index_module.py   전처리 및 모델 로딩
scripts/
  train_kmeans.py       학습 스크립트
  predict_kmeans.py     간단한 예측 함수 예제
  models/               학습된 파이프라인 저장 위치
notebooks/              데이터 분석 및 학습 자료
```

## 학습하기

`notebooks/labeled_sensor_data.csv` 데이터셋을 이용해 `scripts/train_kmeans.py`를 실행하면
`scripts/models/kmeans_pipeline.pkl` 파일이 생성됩니다. 모델은 CO2, 온도, 습도, 면적당 CO2 농도를 입력으로 3개의 클러스터를 학습합니다.

```bash
python scripts/train_kmeans.py
```

## API 실행

로컬에서 실행하려면 다음과 같이 `main.py`를 실행합니다.

```bash
python main.py
```

또는 Docker로 실행할 수 있습니다.

```bash
docker compose up -d --build comfort-model-api
```

`RULE_ENGINE_URL` 환경 변수를 통해 예측 결과를 전송할 대상 주소를 지정할 수 있습니다. 기본값은 `http://localhost:10263/api/v1/comfort` 입니다.

### 엔드포인트

- `POST /api/v1/sensor`  : 센서 값을 전송합니다. 한 위치에 대해 `temperature`, `humidity`, `co2` 세 종류의 값이 모두 모이면 쾌적 지수를 계산하여 룰 엔진으로 전송합니다.

예시 요청 본문:

```json
{
  "location": "보드",
  "sensor_type": "temperature",
  "value": 23.4
}
```

- `GET /health` : 단순 헬스 체크용 엔드포인트입니다.

## 배포

`.github/workflows/deploy-comfort-model.yml` 워크플로는 원격 서버로 코드를 복사한 뒤 `docker-compose` 를 이용해 컨테이너를 재시작합니다. `RULE_ENGINE_URL` 등 환경 변수는 `docker-compose.yml`에서 설정합니다.

