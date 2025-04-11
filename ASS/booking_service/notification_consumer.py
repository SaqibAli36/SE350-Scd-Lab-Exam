import os
import json
import pika
from dotenv import load_dotenv

load_dotenv()

AMQP_URL = os.getenv("AMQP_URL")
params = pika.URLParameters(AMQP_URL)

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f" [x] Received notification for Booking ID: {message['booking_id']}, Status: {message['status']}")

try:
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="notifications")

    channel.basic_consume(queue="notifications", on_message_callback=callback, auto_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

except Exception as e:
    print("Error connecting to RabbitMQ:", e)
