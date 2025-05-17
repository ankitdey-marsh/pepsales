from models.mongo import mongo

def send_sms(user_id, message):
    print(f"Sending SMS to {user_id}: {message}")
    mongo.db.notifications.insert_one({
        "user_id": user_id,
        "type": "sms",
        "message": message
    })
