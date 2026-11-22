# kafka_service.py - OPTIONAL Kafka event streaming
# Kafka is switched off by default (KAFKA_ENABLED=false in .env).
# Flow when it is ON:
#   inventory change -> producer publishes event -> consumer reads it -> WebSocket -> dashboard

import json
import threading
import time

from ..config import KAFKA_ENABLED, KAFKA_SERVER, KAFKA_TOPIC
from .websocket_service import manager

producer = None


def get_producer():
    """Create the producer the first time it is needed."""
    global producer
    if producer is None:
        from kafka import KafkaProducer      # imported here so Kafka is not needed when disabled
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return producer


def publish_event(message: dict) -> bool:
    """Send one event to Kafka. Returns False if Kafka is not reachable."""
    try:
        get_producer().send(KAFKA_TOPIC, message)
        return True
    except Exception as error:
        print("Kafka publish failed:", error)
        return False


def consumer_loop():
    """Read events from Kafka and push them to the dashboard.
    If Kafka stops, wait 5 seconds and try to connect again."""
    from kafka import KafkaConsumer
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_SERVER,
                group_id="visionstock-dashboard",
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
            print("Kafka consumer connected")
            for record in consumer:
                manager.broadcast_from_thread(record.value)
        except Exception as error:
            print("Kafka consumer error:", error, "- retrying in 5 seconds")
            time.sleep(5)


def start_consumer():
    if not KAFKA_ENABLED:
        return
    thread = threading.Thread(target=consumer_loop, daemon=True)
    thread.start()
