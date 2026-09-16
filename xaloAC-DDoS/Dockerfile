# xaloAC DDoS Tool - Dockerfile
# by x410m1s0

FROM python:3.12-slim

LABEL maintainer="x410m1s0"
LABEL description="xaloAC DDoS Tool"
LABEL version="1.0"

WORKDIR /app

# Gerekli sistem paketlerini kur
RUN apt-get update && \
    apt-get install -y --no-install-recommends git gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# requirements.txt dosyasını kopyala
COPY requirements.txt .

# Python bağımlılıklarını kur
RUN pip install --no-cache-dir -r requirements.txt

# Tüm dosyaları kopyala
COPY . .

# Çalıştırma
ENTRYPOINT ["python", "start.py"]