FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /root/prayer_bot/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cp -r /app/data/* /root/prayer_bot/data/

CMD ["python", "main.py"]
