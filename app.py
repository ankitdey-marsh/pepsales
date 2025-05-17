from flask import Flask, request, jsonify
from models.mongo import mongo
from services.email_service import send_email
from services.sms_service import send_sms
from services.inapp_service import store_in_app
import uuid

app = Flask(__name__)
app.config.from_object("config")
mongo.init_app(app)

# ----------------------------
# Create User - auto uuid4
# ----------------------------
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    required_fields = ["name", "email", "phone"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if email/phone already exists
    if mongo.db.users.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already registered"}), 409
    if mongo.db.users.find_one({"phone": data["phone"]}):
        return jsonify({"error": "Phone already registered"}), 409

    user_id = str(uuid.uuid4())

    mongo.db.users.insert_one({
        "_id": user_id,
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"]
    })

    return jsonify({"message": "User created", "user_id": user_id}), 201

# ----------------------------
# Send Notification by method
# ----------------------------
@app.route("/notifications", methods=["POST"])
def send_notification():
    data = request.json
    msg_type = data.get("type")      # email, sms, inapp
    recipient = data.get("recipient")  # email, phone, or user_id
    message = data.get("message")

    if not all([msg_type, recipient, message]):
        return jsonify({"error": "Missing fields"}), 400

    # Fetch user based on recipient type
    if msg_type == "email":
        user = mongo.db.users.find_one({"email": recipient})
    elif msg_type == "sms":
        user = mongo.db.users.find_one({"phone": recipient})
    elif msg_type == "inapp":
        user = mongo.db.users.find_one({"_id": recipient})
    else:
        return jsonify({"error": "Invalid notification type"}), 400

    if not user:
        return jsonify({"error": "Recipient not found"}), 404

    user_id = user["_id"]

    if msg_type == "email":
        send_email(user_id, message)
    elif msg_type == "sms":
        send_sms(user_id, message)
    elif msg_type == "inapp":
        store_in_app(user_id, message)

    return jsonify({"status": f"{msg_type} notification sent"}), 200

# ----------------------------
# Get Notifications for user
# ----------------------------
@app.route("/users/<user_id>/notifications", methods=["GET"])
def get_user_notifications(user_id):
    if not mongo.db.users.find_one({"_id": user_id}):
        return jsonify({"error": "User not found"}), 404

    notifications = mongo.db.notifications.find({"user_id": user_id})
    return jsonify([{
        "type": n["type"],
        "message": n["message"]
    } for n in notifications])

if __name__ == "__main__":
    app.run(debug=True)
