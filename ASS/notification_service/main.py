from flask import Flask, request, jsonify, render_template
import pika
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.json_util import dumps
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["notification_db"]
notifications_collection = db["notifications"]

# RabbitMQ connection
def send_to_queue(notification):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue='notifications')
        channel.basic_publish(exchange='', routing_key='notifications', body=str(notification))
        connection.close()
    except Exception as e:
        print(f"Error sending to RabbitMQ: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notifications', methods=['GET'])
def get_notifications():
    notifications = list(notifications_collection.find({}))
    return dumps(notifications)

@app.route('/send_notification', methods=['POST'])
def send_notification():
    data = request.json
    if not data or 'title' not in data or 'message' not in data:
        return jsonify({"error": "Invalid data"}), 400

    notification = {"title": data['title'], "message": data['message']}
    send_to_queue(notification)
    notifications_collection.insert_one(notification)

    return jsonify({"message": "Notification sent successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
