FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static at build so startup only needs migrate + serve.
RUN python manage.py collectstatic --noinput

EXPOSE 8080

# Cloud Run injects $PORT (8080). Run migrations on start, then serve.
CMD python manage.py migrate --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
