import os
import json
import requests
import pika
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from supabase import create_client, Client
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase Successfully!")
except Exception as e:
    print(f"❌ Supabase Connection Failed: {e}")
    supabase = None

# ✅ RabbitMQ Connection
AMQP_URL = os.getenv("AMQP_URL")
try:
    params = pika.URLParameters(AMQP_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="notifications")
    print("✅ Connected to RabbitMQ")
except Exception as e:
    print("❌ Failed to connect to RabbitMQ:", e)
    connection = None
    channel = None

# ✅ Event Service URL
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL")

# ✅ Flask App Initialization
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")


# ✅ **Landing Page (Fetch Events)**
@app.route("/", methods=["GET"])
def index():
    try:
        response = requests.get(f"{EVENT_SERVICE_URL}/events")
        events = response.json().get("events", []) if response.status_code == 200 else []
    except Exception as e:
        events = []
        flash(f"Error fetching events: {str(e)}", "danger")

    return render_template("index.html", events=events)


# ✅ **Book Tickets**
@app.route("/bookings", methods=["POST"])
def create_booking():
    if not supabase or not channel:
        return jsonify({"message": "Service unavailable"}), 503

    user_id = request.form.get("user_id")
    event_id = request.form.get("event_id")
    tickets = request.form.get("tickets")

    if not user_id or not event_id or not tickets:
        flash("Missing required fields", "danger")
        return redirect(url_for("index"))

    try:
        # Insert into Supabase
        booking_data = {"user_id": user_id, "event_id": event_id, "tickets": int(tickets)}
        response = supabase.table("bookings").insert(booking_data).execute()

        if response.data:
            booking_id = response.data[0]["id"]
            message = json.dumps({"booking_id": booking_id, "status": "CONFIRMED"})
            channel.basic_publish(exchange="", routing_key="notifications", body=message)
            flash("Booking confirmed!", "success")
        else:
            flash("Booking failed!", "danger")

    except Exception as e:
        flash(f"Booking failed: {str(e)}", "danger")

    return redirect(url_for("confirmation"))


# ✅ **Booking Confirmation Page**
@app.route("/confirmation", methods=["GET"])
def confirmation():
    if not supabase:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        response = supabase.table("bookings").select("*").execute()
        bookings = response.data if response.data else []
    except Exception as e:
        bookings = []
        flash(f"Error fetching bookings: {str(e)}", "danger")

    return render_template("confirmation.html", bookings=bookings)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
