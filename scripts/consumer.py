import json

from confluent_kafka import Consumer

from config.config import TOPIC_NAME
from config.logging_config import setup_logging
from scripts.scraper import OfferSearch

def consume_messages():
    logger = setup_logging()

    kafka_config = {
        'bootstrap.servers': 'kafka:9092',
        'group.id': 'scraping_group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
    }

    consumer = Consumer(kafka_config)
    consumer.subscribe([TOPIC_NAME])

    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            logger.error(f"Kafka error: {msg.error()}")
            continue

        data = msg.value().decode('utf-8')
        json_data = json.loads(data)

        instance_search = OfferSearch(json_data, consumer)
        instance_search.start_scraping()

if __name__ == "__main__":
    consume_messages()