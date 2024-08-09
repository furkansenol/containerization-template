import os

from bson import ObjectId
from flask import Flask, request
from pymongo import MongoClient, ReturnDocument
from structlog import get_logger

logger = get_logger()

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")

# MongoDB setup
client = MongoClient(database_url)
db = client["pia"]
collection = db["users"]


@app.route("/users", methods=["POST"])
def post_user():
    new_data = request.json
    insert_result = collection.insert_one(new_data)
    logger.info(f"Inserted data: {new_data}")

    return {
        "status": f"Data inserted successfully with id: {insert_result.inserted_id}"
    }


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id: str):
    user = collection.find_one({"_id": ObjectId(user_id)})

    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
        logger.info(f"Fetched user: {user}")

    return {"user": user} if user else {"status": "Object not found"}


@app.route("/users/<user_id>", methods=["PATCH"])
def update_user(user_id: str):
    update_data = request.json
    updated_user = collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    if not updated_user:
        return {"status": "Object not found"}

    logger.info(f"Updated user: {updated_user}")
    return {"status": "Data updated successfully"}


@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    collection.delete_one({"_id": ObjectId(user_id)})
    logger.info(f"Deleted user with id: {user_id}")

    return {"status": "User deleted successfully"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
