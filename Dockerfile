# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para datos y archivos
RUN mkdir -p /app/data

# Variables de entorno por defecto (solo las no críticas)
ENV ENVIRONMENT=production \
    DEBUG=false \
    HOST=0.0.0.0 \
    PORT=8000 \
    DATA_DIR=/app/data \
    LOG_LEVEL=INFO \
    DEFAULT_LIMIT=100

# Exponer el puerto
EXPOSE ${PORT}

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "${HOST}", "--port", "${PORT}", "--workers", "4"]
