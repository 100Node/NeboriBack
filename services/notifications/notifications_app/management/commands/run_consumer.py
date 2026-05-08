import json
import pika
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from notifications_app.models import Notification

class Command(BaseCommand):
    help = 'Starts the RabbitMQ consumer for notifications'

    def handle(self, *args, **options):
        self.stdout.write("Starting Notifications consumer...")
        
        while True:
            try:
                connection = self.get_rabbitmq_connection()
                channel = connection.channel()
                
                channel.queue_declare(queue='user_registered', durable=True)
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue='user_registered', on_message_callback=self.callback)

                self.stdout.write(self.style.SUCCESS("Notifications consumer started. Waiting for messages..."))
                channel.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                self.stdout.write(self.style.WARNING("Connection lost, reconnecting in 5 seconds..."))
                time.sleep(5)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Consumer error: {e}"))
                time.sleep(5)

    def get_rabbitmq_connection(self):
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASS
        )
        parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        return pika.BlockingConnection(parameters)

    def callback(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            event = data.get('event')
            user_id = data.get('user_id')
            username = data.get('username')

            if event == 'user_registered':
                message = f"Welcome {username}! Your account has been successfully created."
                Notification.objects.create(user_id=user_id, message=message)
                self.stdout.write(self.style.SUCCESS(f"Created notification for user {user_id}"))
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing message: {e}"))
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
