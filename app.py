from flask import Flask, request, jsonify
from models.mongo import mongo
from services.email_service import send_email
from services.sms_service import send_sms
from services.inapp_service import store_in_app

app = Flask(__name__)
app.config.from_object("config")
mongo.init_app(app)

# ---------------------------------------
# POST /users - Create a new user
# ---------------------------------------
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    required_fields = ["user_id", "name", "email", "phone"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if user already exists
    if mongo.db.users.find_one({"_id": data["user_id"]}):
        return jsonify({"error": "User ID already exists"}), 409

    # Insert user into MongoDB
    mongo.db.users.insert_one({
        "_id": data["user_id"],
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"]
    })

    return jsonify({"message": "User created successfully"}), 201

# ---------------------------------------
# POST /notifications - Send a notification
# ---------------------------------------
@app.route("/notifications", methods=["POST"])
def send_notification():
    data = request.json
    user_id = data.get("user_id")
    msg_type = data.get("type")
    message = data.get("message")

    if not all([user_id, msg_type, message]):
        return jsonify({"error": "Missing fields"}), 400

    # Check if user exists
    if not mongo.db.users.find_one({"_id": user_id}):
        return jsonify({"error": "User not found"}), 404

    if msg_type == "email":
        send_email(user_id, message)
    elif msg_type == "sms":
        send_sms(user_id, message)
    elif msg_type == "inapp":
        store_in_app(user_id, message)
    else:
        return jsonify({"error": "Invalid notification type"}), 400

    return jsonify({"status": "Notification sent"}), 200

# ---------------------------------------
# GET /users/<user_id>/notifications
# ---------------------------------------
@app.route("/users/<user_id>/notifications", methods=["GET"])
def get_user_notifications(user_id):
    # Check if user exists
    if not mongo.db.users.find_one({"_id": user_id}):
        return jsonify({"error": "User not found"}), 404

    notifications = mongo.db.notifications.find({"user_id": user_id})
    return jsonify([{
        "type": n["type"],
        "message": n["message"]
    } for n in notifications])

if __name__ == "__main__":
    app.run(debug=True)
