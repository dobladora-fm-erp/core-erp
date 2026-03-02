# Usamos la imagen oficial de Python 3.12 (ligera)
FROM python:3.12-slim

# Evita que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python guarde en buffer la salida estándar (para ver los logs en tiempo real)
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para PostgreSQL
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean

# Copiamos e instalamos las librerías de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiamos el resto del proyecto
COPY . /app/
