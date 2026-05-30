FROM python:3.11-slim

# Dependencias del sistema para opencv-headless y otras libs nativas
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# PYTHONPATH apunta a /app para que los imports absolutos funcionen
ENV PYTHONPATH=/app

# Instalar PyTorch CPU-only ANTES de requirements.txt
# (evita descargar la versión GPU de ~2 GB que pip elige por defecto)
RUN pip install --no-cache-dir torch \
    --index-url https://download.pytorch.org/whl/cpu

# Instalar dependencias de la aplicación
# (se copian primero para aprovechar la caché de Docker si el código cambia)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Crear directorios de runtime que el pipeline espera encontrar
RUN mkdir -p data/fichas data/samples data/chroma data/icanh_docs

EXPOSE 8000

# Railway sobreescribe este CMD con startCommand del railway.json
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
