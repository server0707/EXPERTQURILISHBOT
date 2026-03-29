FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# DB fayli uchun volume mount nuqtasi
VOLUME ["/app/data"]

ENV DB_PATH=/app/data/bot.db

CMD ["python", "main.py"]
