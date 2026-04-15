import os
import uuid
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:////data/app.db",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


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


@app.get("/")
def index():
    return "Hello from Flask!"


@app.post("/data")
def create_data():
    payload = request.get_json(silent=True) or {}
    description = payload.get("description")

    if not isinstance(description, str) or not description.strip():
        return jsonify({"error": "description is required"}), 400

    data = Data(description=description.strip())
    db.session.add(data)
    db.session.commit()

    return jsonify(data.to_dict()), 201


@app.get("/data")
def list_data():
    data_items = db.session.execute(db.select(Data).order_by(Data.id)).scalars()
    return jsonify([data.to_dict() for data in data_items])


@app.get("/data/<data_id>")
def get_data(data_id):
    data = db.get_or_404(Data, data_id)
    return jsonify(data.to_dict())


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
