import json
import os
from typing import Any

from kafka import KafkaProducer


class KafkaProducerAdapter:
    """
    Kafka producer adapter.

    Converts Python dictionaries to JSON before publishing to Kafka.
    """

    def __init__(self, bootstrap_servers: str | None = None) -> None:
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:9092",
        )

        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )

    def send(self, topic: str, value: dict[str, Any]) -> None:
        self.producer.send(
            topic,
            value=value,
        )

    def flush(self) -> None:
        self.producer.flush()

    def close(self) -> None:
        self.producer.close()