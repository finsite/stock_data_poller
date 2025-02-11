from unittest.mock import patch
from app.queue.queue_sender import QueueSender


@patch("boto3.client")
def test_sqs_queue_sender(mock_boto3):
    mock_boto3.return_value.send_message.return_value = {"MessageId": "12345"}
    sender = QueueSender(queue_type="sqs", queue_url="http://fake-sqs-url")
    sender.send_message({"key": "value"})

    mock_boto3.return_value.send_message.assert_called_once_with(
        QueueUrl="http://fake-sqs-url",
        MessageBody='{"key": "value"}',
    )


@patch("pika.BlockingConnection")
def test_rabbitmq_queue_sender(mock_pika):
    sender = QueueSender(queue_type="rabbitmq", queue_url="amqp://guest:guest@localhost:5672/")
    sender.send_message({"key": "value"})

    mock_channel = mock_pika.return_value.channel.return_value
    mock_channel.basic_publish.assert_called_once()
