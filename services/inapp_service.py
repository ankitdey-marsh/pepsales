from models.mongo import mongo

def store_in_app(user_id, message):
    print(f"Storing IN-APP notification for {user_id}: {message}")
    mongo.db.notifications.insert_one({
        "user_id": user_id,
        "type": "inapp",
        "message": message
    })
