from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# ✅ MongoDB Connection
try:
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        raise ValueError("❌ MONGO_URL is missing in environment variables!")

    client = MongoClient(mongo_url)
    db = client.get_database()
    events_collection = db["events"]
    print("✅ MongoDB Connected Successfully!")

except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    exit(1)  # Stop app if MongoDB connection fails

# ✅ Serve the frontend (events.html)
@app.route("/")
def home():
    return render_template("events.html")  # Ensure the file exists in 'templates/' folder

# ✅ Route to GET all events
@app.route("/events", methods=["GET"])
def get_events():
    if events_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    events = list(events_collection.find({}, {"_id": 1, "name": 1, "date": 1, "location": 1, "available_tickets": 1}))
    # Convert `_id` to string before sending to frontend
    for event in events:
        event["_id"] = str(event["_id"])

    return jsonify({"events": events})

# ✅ Route to ADD a new event (Prevents Duplicates)
@app.route("/events", methods=["POST"])
def add_event():
    if events_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    required_fields = ["name", "date", "location", "available_tickets"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Check for duplicate event name
    existing_event = events_collection.find_one({"name": data["name"]})
    if existing_event:
        return jsonify({"error": "Event with this name already exists!"}), 409

    new_event = {
        "name": data["name"],
        "date": data["date"],
        "location": data["location"],
        "available_tickets": int(data["available_tickets"])
    }
    result = events_collection.insert_one(new_event)

    return jsonify({"message": "Event added successfully", "inserted_id": str(result.inserted_id)}), 201

# ✅ Route to DELETE an event (Use `_id`)
@app.route("/events/<string:event_id>", methods=["DELETE"])
def delete_event(event_id):
    if events_collection is None:
        return jsonify({"error": "Database connection failed"}), 500

    result = events_collection.delete_one({"_id": event_id})  # Delete by `_id`
    
    if result.deleted_count == 0:
        return jsonify({"error": "Event not found"}), 404

    return jsonify({"message": "Event deleted successfully!"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)  # Allows external connections
