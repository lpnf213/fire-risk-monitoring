import json
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from confluent_kafka import Producer

BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC: str = os.getenv("KAFKA_TOPIC", "env_raw_sensors")

@dataclass
class Zone:
    zone_id: str
    lat: float
    lon: float
    vegetation: str

ZONES: List[Zone] = [
    Zone(zone_id="ZONE_A", lat=40.123, lon=-8.456, vegetation="pine"),
    Zone(zone_id="ZONE_B", lat=40.200, lon=-8.500, vegetation="brush"),
    Zone(zone_id="ZONE_C", lat=40.050, lon=-8.400, vegetation="mixed"),
]

SENSORS_PER_ZONE: int = 3

def create_producer() -> Producer:
    return Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})

def base_env_for_zone(zone_id: str) -> Tuple[float, float, float]:
    """
    Return baseline (temp_c, humidity_rel, soil_moisture) for a given zone.
    """
    if zone_id == "ZONE_A":
        return 30.0, 35.0, 0.25
    if zone_id == "ZONE_B":
        return 28.0, 40.0, 0.30
    if zone_id == "ZONE_C":
        return 26.0, 45.0, 0.35
    return 27.0, 40.0, 0.30

def build_event(sensor_id: str, zone: Zone) -> Dict[str, object]:
    """
    Build a single sensor event for a given sensor and zone.
    """

    base_temp: float
    base_hum: float
    base_soil: float
    base_temp, base_hum, base_soil = base_env_for_zone(zone.zone_id)

    temp: float = base_temp + random.uniform(-1.5, 1.5)
    humidity: float = max(5.0, min(90.0, base_hum + random.uniform(-5.0, 5.0)))
    soil_moisture: float = max(0.02, min(0.5, base_soil + random.uniform(-0.02, 0.02)))
    smoke_ppm: float = max(0.0, random.gauss(0.5, 0.5))
    wind_speed: float = max(0.0, random.gauss(10.0, 3.0))

    # Occasionally simulate a fire-like pattern
    if random.random() < 0.02:  # 2% chance
        temp += random.uniform(10.0, 20.0)
        humidity -= random.uniform(10.0, 20.0)
        smoke_ppm += random.uniform(5.0, 15.0)
        wind_speed += random.uniform(5.0, 15.0)

    event: Dict[str, object] = {
        "sensor_id": sensor_id,
        "zone_id": zone.zone_id,
        "lat": zone.lat + random.uniform(-0.001, 0.001),
        "lon": zone.lon + random.uniform(-0.001, 0.001),
        "temp_c": round(temp, 2),
        "humidity_rel": round(humidity, 2),
        "soil_moisture": round(soil_moisture, 3),
        "smoke_ppm": round(smoke_ppm, 3),
        "wind_speed_kmh": round(wind_speed, 2),
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "source": "SENSOR_SIMULATOR",
    }
    return event

def delivery_report(err: Exception | None, msg) -> None:
    if err is not None:
        print(f"❌ Delivery failed for record {msg.key()}: {err}")

def main() -> None:
    print(f"🚀 Starting sensor simulator → {BOOTSTRAP_SERVERS} topic={TOPIC}")
    producer: Producer = create_producer()

    sensors: List[Dict[str, object]] = []
    for zone in ZONES:
        for i in range(SENSORS_PER_ZONE):
            sensors.append(
                {
                    "sensor_id": f"{zone.zone_id}_S{i+1}",
                    "zone": zone,
                }
            )

    while True:
        for sensor in sensors:
            sensor_id: str = sensor["sensor_id"]  # type: ignore[assignment]
            zone: Zone = sensor["zone"]           # type: ignore[assignment]
            event: Dict[str, object] = build_event(sensor_id, zone)

            payload: bytes = json.dumps(event).encode("utf-8")
            key: bytes = str(event["zone_id"]).encode("utf-8")

            producer.produce(
                TOPIC,
                key=key,
                value=payload,
                callback=delivery_report,
            )


        producer.poll(0)
        producer.flush(5)
        time.sleep(2)


if __name__ == "__main__":
    main()
