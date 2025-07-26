FROM python:3.8-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cambiar el CMD para incluir el argumento requerido
CMD ["python", "main.py", "--mode", "backtest"]
