"""Flask application: serves the static frontend and the JSON API."""

from dotenv import load_dotenv
from flask import Flask, jsonify

from . import db

# Reads DATABASE_URL from the local .env file. On Render there is no .env file;
# the variable is set in the environment and load_dotenv() leaves it untouched.
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/health")
def health():
    try:
        db.check_connection()
    except Exception:
        app.logger.exception("Database check failed")
        return jsonify(status="error", database="unreachable"), 503
    return jsonify(status="ok", database="ok")


# Create the tables on startup. If the database is unreachable, the app fails
# to start, which makes the problem visible immediately in the Render logs.
db.init_schema()
