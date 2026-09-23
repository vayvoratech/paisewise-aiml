from unittest.mock import Mock, patch

from app.integrations.kafka_producer import KafkaProducerAdapter


@patch("app.integrations.kafka_producer.KafkaProducer")
def test_kafka_producer_send(mock_kafka_producer) -> None:
    producer = Mock()
    mock_kafka_producer.return_value = producer

    adapter = KafkaProducerAdapter("localhost:9092")

    payload = {
        "user_id": "user-123",
        "churn_score": 0.85,
        "message": "Complete your investment journey today.",
    }

    adapter.send("notifications.push", payload)

    producer.send.assert_called_once_with(
        "notifications.push",
        value=payload,
    )


@patch("app.integrations.kafka_producer.KafkaProducer")
def test_kafka_producer_flush(mock_kafka_producer) -> None:
    producer = Mock()
    mock_kafka_producer.return_value = producer

    adapter = KafkaProducerAdapter("localhost:9092")

    adapter.flush()

    producer.flush.assert_called_once()


@patch("app.integrations.kafka_producer.KafkaProducer")
def test_kafka_producer_close(mock_kafka_producer) -> None:
    producer = Mock()
    mock_kafka_producer.return_value = producer

    adapter = KafkaProducerAdapter("localhost:9092")

    adapter.close()

    producer.close.assert_called_once()
    