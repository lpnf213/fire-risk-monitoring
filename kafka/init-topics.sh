#!/bin/bash
echo "waiting for kafka to be ready..."

# wait for broker 
until kafka-topics --bootstrap-server kafka:9092 --list >/dev/null 2>&1; do
    echo "Kafka not ready yet ... retrying in 5s"
    sleep 5s
done

echo "kafka is ready. Creating topics if they don't exist..."

kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists \
  --topic env_raw_sensors --partitions 3 --replication-factor 1

kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists \
  --topic env_weather --partitions 3 --replication-factor 1

kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists \
  --topic fire_alerts --partitions 1 --replication-factor 1

echo "✅ All Kafka topics created."

# keep container alive so you can see logs if needed
tail -f /dev/null