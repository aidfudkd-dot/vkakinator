FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["gunicorn", "--workers=4", "--threads=2", "--worker-class=gthread", "--bind=0.0.0.0:8000", "app:app"]