FROM python:3.12-slim-bullseye

# Carpeta de trabajo dentro del container
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copiar el código de la API
COPY app/ ./app/

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]