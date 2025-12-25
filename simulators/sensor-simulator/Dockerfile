FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir confluent-kafka

COPY main.py .

ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV KAFKA_TOPIC=env_raw_sensors

CMD ["python", "main.py"]