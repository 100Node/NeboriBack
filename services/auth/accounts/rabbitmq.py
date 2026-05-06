import os
import json
from django.conf import settings
import pika


def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASS
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)


def publish_message(queue_name: str, message: dict):
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )

    connection.close()
