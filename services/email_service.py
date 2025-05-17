from models.mongo import mongo

def send_email(user_id, message):
    print(f"Sending EMAIL to {user_id}: {message}")
    mongo.db.notifications.insert_one({
        "user_id": user_id,
        "type": "email",
        "message": message
    })
