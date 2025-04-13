from confluent_kafka import Producer
from config.logging_config import setup_logging
from config.config import TOPIC_NAME

class monProducer():

    KAFKA_BROKER = 'kafka:9092'

    def __init__(self):
        self.conf = {
            'bootstrap.servers': self.KAFKA_BROKER
        }
        self.producer = Producer(self.conf)
        self.logger = setup_logging()

    def delivery_report(self, error, message):
        if error is not None:
            self.logger.error(f"Error during message ({message}) delivery: {error}")
        else:
            self.logger.info(f"Message delivered to {message.topic()} [{message.partition()}]")

    def send_message_to_topic(self, subject):
        self.producer.produce(TOPIC_NAME, value=subject, callback=self.delivery_report)
        self.producer.flush()