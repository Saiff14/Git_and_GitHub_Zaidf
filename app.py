from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
import os
import json
import uuid
from hashlib import sha256
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

try:
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri) if mongo_uri else None
    collection = client["todo"]["items"] if client else None
except Exception:
    collection = None


@app.route("/")
def todo():
    return render_template("todo.html")


@app.route("/api")
def api():
    with open("data.json", "r", encoding="utf-8") as file:
        return jsonify(json.load(file))


@app.route("/submittodoitem", methods=["POST"])
@app.route("/submit", methods=["POST"])
def submit_alias():
    return submittodoitem()
def submittodoitem():
    item_name = request.form.get("itemName", "").strip()
    item_description = request.form.get("itemDescription", "").strip()

    if not item_name or not item_description:
        return render_template(
            "todo.html",
            error="Item name and item description are required.",
        ), 400

    item_uuid = str(uuid.uuid4())
    item_hash = sha256(
        f"{item_name}|{item_description}|{item_uuid}".encode("utf-8")
    ).hexdigest()
    item_id = item_hash[:12]

    document = {
        "item_id": item_id,
        "item_uuid": item_uuid,
        "item_hash": item_hash,
        "itemName": item_name,
        "itemDescription": item_description,
    }

    if collection is not None:
        collection.insert_one(document)

    return render_template(
        "todo.html",
        success="To-Do item submitted successfully.",
        item=document,
    )


if __name__ == "__main__":
    app.run(debug=True)
