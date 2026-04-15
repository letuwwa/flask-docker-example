## Run with Docker

Build and start the Flask app:

```bash
docker compose up --build
```

The app listens on <http://localhost:5000>.

Useful checks:

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

By default, the app uses `sqlite:///app.db`.
Set `DATABASE_URL` to use another SQLite path or a different database.
