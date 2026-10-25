"""Flask application: serves the static frontend and the JSON API."""

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from . import db, game, rng

# Reads DATABASE_URL from the local .env file. On Render there is no .env file;
# the variable is set in the environment and load_dotenv() leaves it untouched.
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")

MAX_NAME_LENGTH = 100

# Upper limit of spins per request. Larger simulations are split into several
# requests by the frontend, so a request never runs into Gunicorn's timeout.
MAX_SPINS_PER_REQUEST = 10_000


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


@app.get("/api/configurations")
def list_configurations():
    return jsonify(db.list_configurations())


@app.get("/api/configurations/<int:configuration_id>")
def get_configuration(configuration_id):
    configuration = db.get_configuration(configuration_id)
    if configuration is None:
        return jsonify(error="configuration not found"), 404
    return jsonify(configuration)


def _config_from_request(data):
    """Take reel strips and paytable from a request body and validate them.

    Returns the configuration dict. Raises ValueError with a readable message.
    """
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")
    config = {
        "reel_strips": data.get("reel_strips"),
        "paytable": data.get("paytable"),
    }
    game.validate_config(config)
    return config


@app.post("/api/configurations/evaluate")
def evaluate_configuration():
    """Calculate the theoretical values of a configuration without saving it."""
    try:
        config = _config_from_request(request.get_json(silent=True))
    except ValueError as error:
        return jsonify(error=str(error)), 400
    return jsonify(game.theoretical_stats(config))


@app.post("/api/configurations")
def create_configuration():
    """Save a new configuration (decision 0007: saved configurations are never
    changed; editing means saving a new one)."""
    data = request.get_json(silent=True)
    try:
        config = _config_from_request(data)
    except ValueError as error:
        return jsonify(error=str(error)), 400

    name = data.get("name")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= MAX_NAME_LENGTH:
        return jsonify(error=f"name must have 1 to {MAX_NAME_LENGTH} characters"), 400

    configuration_id = db.insert_configuration(name.strip(), config)
    return jsonify(db.get_configuration(configuration_id)), 201


def _is_int(value):
    # bool is a subclass of int in Python, so True would pass as 1.
    return isinstance(value, int) and not isinstance(value, bool)


@app.post("/api/spins")
def create_spins():
    """Execute and store spins.

    Request:  {"configuration_id": 1, "mode": "manual"}
              {"configuration_id": 1, "mode": "auto", "count": 100}
    manual: exactly 1 spin, random.org with fallback to Python.
    auto:   1 to MAX_SPINS_PER_REQUEST spins, Python.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="request body must be a JSON object"), 400

    configuration_id = data.get("configuration_id")
    mode = data.get("mode")
    count = data.get("count", 1)

    if not _is_int(configuration_id):
        return jsonify(error="configuration_id must be an integer"), 400
    if mode not in ("manual", "auto"):
        return jsonify(error="mode must be 'manual' or 'auto'"), 400
    if not _is_int(count) or not 1 <= count <= MAX_SPINS_PER_REQUEST:
        return jsonify(
            error=f"count must be an integer from 1 to {MAX_SPINS_PER_REQUEST}"
        ), 400
    if mode == "manual" and count != 1:
        return jsonify(error="mode 'manual' allows exactly 1 spin"), 400

    configuration = db.get_configuration(configuration_id)
    if configuration is None:
        return jsonify(error="configuration not found"), 404

    if mode == "manual":
        lengths = [len(strip) for strip in configuration["reel_strips"]]
        stops, source = rng.manual_stop_positions(lengths)
        results = [game.spin(configuration, lambda _lengths: stops)]
    else:
        source = rng.PYTHON
        results = [
            game.spin(configuration, rng.python_stop_positions) for _ in range(count)
        ]

    db.insert_spins(configuration_id, results, source)

    return jsonify(
        configuration_id=configuration_id,
        rng_source=source,
        count=len(results),
        total_bet=sum(result["bet"] for result in results),
        total_payout=sum(result["payout"] for result in results),
        spins=results,
    ), 201


# Create the tables and the default configuration on startup (decisions 0010
# and 0013). If the database is unreachable, the app fails to start, which
# makes the problem visible immediately in the Render logs.
db.init_schema()
db.ensure_default_configuration(game.DEFAULT_CONFIG_NAME, game.DEFAULT_CONFIG)
