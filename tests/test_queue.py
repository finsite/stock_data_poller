"""
Tests for the QueueSender class.

This module contains unit tests for the QueueSender class, which is responsible for
sending messages to SQS or RabbitMQ queues.
"""

from unittest.mock import patch

import pika
import pytest

from app.message_queue.queue_sender import QueueSender


@patch("boto3.client")
def test_sqs_queue_sender(mock_boto3):
    """Test sending messages to SQS queue using QueueSender."""
    mock_boto3.return_value.send_message.return_value = {"MessageId": "12345"}

    # Patch config functions
    with (
        patch("app.message_queue.queue_sender.get_queue_type", return_value="sqs"),
        patch(
            "app.message_queue.queue_sender.get_sqs_queue_url",
            return_value="http://fake-sqs-url",
        ),
    ):

        sender = QueueSender()
        sender.send_message({"key": "value"})

        mock_boto3.return_value.send_message.assert_called_once_with(
            QueueUrl="http://fake-sqs-url",
            MessageBody='{"key": "value"}',
        )


@patch("pika.BlockingConnection")
def test_rabbitmq_queue_sender(mock_pika):
    """Test sending messages to RabbitMQ using QueueSender."""
    with (
        patch("app.message_queue.queue_sender.get_queue_type", return_value="rabbitmq"),
        patch("app.message_queue.queue_sender.get_rabbitmq_user", return_value="guest"),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_password", return_value="guest"
        ),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_host", return_value="localhost"
        ),
        patch("app.message_queue.queue_sender.get_rabbitmq_port", return_value=5672),
        patch("app.message_queue.queue_sender.get_rabbitmq_vhost", return_value="/"),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_exchange",
            return_value="stock_data_exchange",
        ),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_routing_key",
            return_value="stock_data",
        ),
    ):

        sender = QueueSender()
        sender.send_message({"key": "value"})

        mock_channel = mock_pika.return_value.channel.return_value
        mock_channel.basic_publish.assert_called_once_with(
            exchange="stock_data_exchange",
            routing_key="stock_data",
            body='{"key": "value"}',
            properties=pika.BasicProperties(delivery_mode=2),
        )


@patch("boto3.client")
def test_sqs_queue_sender_failure(mock_boto3):
    """Test handling errors when sending a message to SQS."""
    mock_boto3.return_value.send_message.side_effect = Exception("SQS send failed")

    with (
        patch("app.message_queue.queue_sender.get_queue_type", return_value="sqs"),
        patch(
            "app.message_queue.queue_sender.get_sqs_queue_url",
            return_value="http://fake-sqs-url",
        ),
    ):

        sender = QueueSender()

        with pytest.raises(Exception):
            sender.send_message({"key": "value"})


@patch("pika.BlockingConnection")
def test_rabbitmq_queue_sender_failure(mock_pika):
    """Test handling errors when sending a message to RabbitMQ."""
    mock_channel = mock_pika.return_value.channel.return_value
    mock_channel.basic_publish.side_effect = Exception("RabbitMQ send failed")

    with (
        patch("app.message_queue.queue_sender.get_queue_type", return_value="rabbitmq"),
        patch("app.message_queue.queue_sender.get_rabbitmq_user", return_value="guest"),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_password", return_value="guest"
        ),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_host", return_value="localhost"
        ),
        patch("app.message_queue.queue_sender.get_rabbitmq_port", return_value=5672),
        patch("app.message_queue.queue_sender.get_rabbitmq_vhost", return_value="/"),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_exchange",
            return_value="stock_data_exchange",
        ),
        patch(
            "app.message_queue.queue_sender.get_rabbitmq_routing_key",
            return_value="stock_data",
        ),
    ):

        sender = QueueSender()

        with pytest.raises(Exception):
            sender.send_message({"key": "value"})
