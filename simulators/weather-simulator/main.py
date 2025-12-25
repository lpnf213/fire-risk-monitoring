import json
import os
import random
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from confluent_kafka import Producer

BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC: str = os.getenv("KAFKA_TOPIC", "env_weather")

ZONES: List[str] = ["ZONE_A", "ZONE_B", "ZONE_C"]

def create_producer() -> Producer:
    return Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})


def base_weather_for_zone(zone_id: str) -> Tuple[float, float, float]:
    """
    Return baseline (temp_c, humidity_rel, wind_speed_kmh) for a given zone.
    """
    if zone_id == "ZONE_A":
        return 30.0, 35.0, 15.0
    if zone_id == "ZONE_B":
        return 28.0, 40.0, 10.0
    if zone_id == "ZONE_C":
        return 26.0, 45.0, 8.0
    return 27.0, 40.0, 10.0


def build_event(zone_id: str) -> Dict[str, object]:
    """
    Build a single weather event for a given zone.
    """
    base_temp: float
    base_hum: float
    base_wind: float
    base_temp, base_hum, base_wind = base_weather_for_zone(zone_id)

    temp: float = base_temp + random.uniform(-1.0, 1.0)
    humidity: float = max(5.0, min(95.0, base_hum + random.uniform(-5.0, 5.0)))
    wind_speed: float = max(0.0, base_wind + random.uniform(-3.0, 5.0))
    wind_dir: float = random.uniform(0.0, 360.0)

    event: Dict[str, object] = {
        "zone_id": zone_id,
        "temp_c": round(temp, 2),
        "humidity_rel": round(humidity, 2),
        "wind_speed_kmh": round(wind_speed, 2),
        "wind_direction_deg": round(wind_dir, 2),
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "source": "WEATHER_SIMULATOR",
    }
    return event


def delivery_report(err: Exception | None, msg) -> None:
    if err is not None:
        print(f"❌ Delivery failed for record {msg.key()}: {err}")

def main() -> None:
    print(f"🌦️  Starting weather simulator → {BOOTSTRAP_SERVERS} topic={TOPIC}")
    producer: Producer = create_producer()

    while True:
        for zone_id in ZONES:
            event: Dict[str, object] = build_event(zone_id)
            payload: bytes = json.dumps(event).encode("utf-8")
            key: bytes = zone_id.encode("utf-8")

            producer.produce(
                TOPIC,
                key=key,
                value=payload,
                callback=delivery_report,
            )

        producer.poll(0)
        producer.flush(5)
        time.sleep(10)

if __name__ == "__main__":
    main()