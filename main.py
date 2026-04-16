import os
import uuid
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'app.db'}",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGO_DATABASE_URL") or "mongodb://localhost:27017/app"
mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
mongo_db = mongo_client.get_default_database()
mongo_data = mongo_db["data"]


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Data(db.Model):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    description: Mapped[str] = mapped_column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
        }


def mongo_document_to_dict(document):
    return {
        "id": document["id"],
        "description": document["description"],
    }


@app.get("/")
def index():
    return "Hello from Flask!"


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/data")
def create_data():
    payload = request.get_json(silent=True) or {}
    description = payload.get("description")

    if not isinstance(description, str) or not description.strip():
        return jsonify({"error": "description is required"}), 400

    record = {
        "id": str(uuid.uuid4()),
        "description": description.strip(),
    }
    data = Data(**record)
    db.session.add(data)

    try:
        mongo_data.insert_one(record)
        db.session.commit()
    except PyMongoError as error:
        db.session.rollback()
        return jsonify({"error": "failed to save record to MongoDB", "details": str(error)}), 503
    except Exception:
        db.session.rollback()
        mongo_data.delete_one({"id": record["id"]})
        raise

    return jsonify(data.to_dict()), 201


@app.get("/data")
def list_data():
    data_items = db.session.execute(db.select(Data).order_by(Data.id)).scalars()
    return jsonify([data.to_dict() for data in data_items])


@app.get("/data/<data_id>")
def get_data(data_id):
    data = db.get_or_404(Data, data_id)
    return jsonify(data.to_dict())


@app.get("/mongo/data")
def list_mongo_data():
    data_items = mongo_data.find({}, {"_id": False}).sort("id", 1)
    return jsonify([mongo_document_to_dict(data) for data in data_items])


@app.get("/mongo/data/<data_id>")
def get_mongo_data(data_id):
    data = mongo_data.find_one({"id": data_id}, {"_id": False})

    if data is None:
        return jsonify({"error": "not found"}), 404

    return jsonify(mongo_document_to_dict(data))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
