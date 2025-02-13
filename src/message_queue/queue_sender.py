import os
import pika  # For RabbitMQ
import boto3  # For SQS
import json
#from utils.setup_logger import setup_logger
from utils.setup_logger import setup_logger

# Set up logger
logger = setup_logger()

class QueueSender:
    def __init__(self, queue_type, queue_url=None, rabbitmq_host=None, rabbitmq_exchange=None, rabbitmq_routing_key=None):
        self.queue_type = queue_type
        self.queue_url = queue_url
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_exchange = rabbitmq_exchange
        self.rabbitmq_routing_key = rabbitmq_routing_key
        
        if self.queue_type == "rabbitmq":
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.rabbitmq_exchange, exchange_type='direct')
        elif self.queue_type == "sqs":
            self.sqs = boto3.client('sqs')
        else:
            raise ValueError("Unsupported queue type")

    def send(self, data):
        """
        Send data to the appropriate queue (SQS or RabbitMQ).
        """
        try:
            if self.queue_type == "rabbitmq":
                message_body = json.dumps(data)
                self.channel.basic_publish(
                    exchange=self.rabbitmq_exchange,
                    routing_key=self.rabbitmq_routing_key,
                    body=message_body
                )
                logger.info(f"Data sent to RabbitMQ exchange {self.rabbitmq_exchange} with routing key {self.rabbitmq_routing_key}")
            elif self.queue_type == "sqs":
                message_body = json.dumps(data)
                self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=message_body)
                logger.info(f"Data sent to SQS queue: {self.queue_url}")
        except Exception as e:
            logger.error(f"Error sending data to {self.queue_type}: {e}")

    def close(self):
        if self.queue_type == "rabbitmq":
            self.connection.close()
