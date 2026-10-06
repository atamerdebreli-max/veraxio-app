FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    build-essential \
    libexiv2-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch (CUDA indirmesin - 3 GB tasarruf!)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Diğer bağımlılıklar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodu
COPY . .

# Kalıcı veri için
RUN mkdir -p /app/data

EXPOSE 8501

CMD streamlit run main.py --server.port $PORT --server.address 0.0.0.0