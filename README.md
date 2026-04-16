# Flask Docker Example

A small Flask API that stores submitted data in two databases at the same time:

- SQLite through Flask-SQLAlchemy
- MongoDB through PyMongo

The app runs with Docker Compose. Compose starts one container for the Flask app and one container for MongoDB.

## Technologies

- Python 3.13
- Flask
- Flask-SQLAlchemy
- SQLite
- PyMongo
- MongoDB
- Gunicorn
- Docker Compose
- uv

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///app.db
MONGO_URI=mongodb://admin:secret@mongodb:27017/app?authSource=admin
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=secret
```

Docker Compose reads this file automatically.

Inside Docker Compose, use `mongodb` as the MongoDB hostname because `mongodb` is the service name of the MongoDB container.

## Run with Docker

Build and start the app:

```bash
docker compose up --build
```

The API listens on:

```text
http://localhost:5000
```

## Useful Checks

Check the app:

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

Create a record in both SQLite and MongoDB:

```bash
curl -X POST http://localhost:5000/data \
  -H "Content-Type: application/json" \
  -d '{"description":"saved in both databases"}'
```

Read records from SQLite:

```bash
curl http://localhost:5000/data
```

Read records from MongoDB:

```bash
curl http://localhost:5000/mongo/data
```

## Local Development

Install dependencies:

```bash
uv sync
```

Run the Flask app locally:

```bash
uv run python main.py
```

For local development outside Docker, use `localhost` in `MONGO_URI`:

```env
MONGO_URI=mongodb://admin:secret@localhost:27017/app?authSource=admin
```
