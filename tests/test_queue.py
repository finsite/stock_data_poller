"""
Tests for the QueueSender class.

This module contains unit tests for the QueueSender class, which is responsible for
sending messages to SQS or RabbitMQ queues.
"""

@patch("boto3.client")
def test_sqs_queue_sender(mock_boto3):
    """
    Test sending messages to SQS queue using QueueSender.

    This test mocks the response from SQS and asserts that the send_message method was
    called once with the expected parameters.
    """
    # Mock the response from SQS
    mock_boto3.return_value.send_message.return_value = {"MessageId": "12345"}

    # Initialize QueueSender for SQS
    sender = QueueSender(queue_type="sqs", queue_url="http://fake-sqs-url")

    # Send a mock message
    sender.send_message({"key": "value"})

    # Assert that the send_message method was called once with the expected parameters
    mock_boto3.return_value.send_message.assert_called_once_with(
        QueueUrl="http://fake-sqs-url",
        MessageBody='{"key": "value"}',
    )


@patch("pika.BlockingConnection")
def test_rabbitmq_queue_sender(mock_pika):
    """
    Test sending messages to RabbitMQ queue using QueueSender.

    This test mocks the response from RabbitMQ and asserts that the basic_publish method
    was called once with the expected parameters.
    """
    # Initialize QueueSender for RabbitMQ
    sender = QueueSender(queue_type="rabbitmq", queue_url="amqp://guest:guest@localhost:5672/")

    # Send a mock message
    sender.send_message({"key": "value"})

    # Assert that the basic_publish method was called once with the expected parameters
    mock_channel = mock_pika.return_value.channel.return_value
    mock_channel.basic_publish.assert_called_once()

    # You can add more detailed assertions here based on the actual routing key and message
    mock_channel.basic_publish.assert_called_with(
        exchange="",
        routing_key="stock_data",
        body='{"key": "value"}',
        properties=pika.BasicProperties(delivery_mode=2),  # Persistent message
    )


@patch("boto3.client")
def test_sqs_queue_sender_failure(mock_boto3):
    """
    Test handling errors when sending a message to SQS.

    This test mocks SQS to raise an exception and asserts that the exception is raised
    when attempting to send a message.
    """
    # Mock SQS to raise an exception
    mock_boto3.return_value.send_message.side_effect = Exception("SQS send failed")

    sender = QueueSender(queue_type="sqs", queue_url="http://fake-sqs-url")

    # Assert that the exception is raised when attempting to send a message
    with pytest.raises(Exception):
        sender.send_message({"key": "value"})


@patch("pika.BlockingConnection")
def test_rabbitmq_queue_sender_failure(mock_pika):
    """
    Test handling errors when sending a message to RabbitMQ.

    This test mocks RabbitMQ to raise an exception and asserts that the exception is
    raised when attempting to send a message.
    """
    # Mock RabbitMQ to raise an exception
    mock_channel = mock_pika.return_value.channel.return_value
    mock_channel.basic_publish.side_effect = Exception("RabbitMQ send failed")

    sender = QueueSender(queue_type="rabbitmq", queue_url="amqp://guest:guest@localhost:5672/")

    # Assert that the exception is raised when attempting to send a message
    with pytest.raises(Exception):
        sender.send_message({"key": "value"})
