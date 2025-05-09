FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      python3-dev \
      cmake \
      libatlas-base-dev \
      libgomp1 && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --only-binary=:all: -r requirements.txt

COPY app ./app
COPY scripts ./scripts

CMD ["uvicorn", "app.server.fast_server:app", "--host", "0.0.0.0", "--port", "10264"]
