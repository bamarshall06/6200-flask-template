"""The Flask application.

Run it locally with:

    python app.py          ->  http://127.0.0.1:5000

On the class server this file is not what runs. Dokku reads the Procfile and
starts gunicorn against the same `app` object defined below, so whatever works
here works there.
"""

import os
import secrets

from dotenv import load_dotenv
from flask import Flask, render_template

from database import DatabaseNotConfigured, is_configured

load_dotenv()

app = Flask(__name__)

# A missing secret key is a warning, not a crash. Flask + Routes has no logins and no
# sessions, so refusing to start without one would block the app for two weeks
# for no reason. Set FLASK_SECRET_KEY once you do have logins - a key generated
# at startup is a different key after every restart, which logs everyone out.
_configured_key = os.getenv("FLASK_SECRET_KEY")
app.secret_key = _configured_key or secrets.token_hex(32)
if not _configured_key:
    app.logger.warning(
        "FLASK_SECRET_KEY is not set - using a throwaway key generated at "
        "startup. Sessions will not survive a restart."
    )

# Does a database connection string exist? Nothing connects here; this only
# asks. The Examples page uses it to explain itself when there is no database.
app.config["DATABASE_CONFIGURED"] = is_configured()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/healthz")
def healthz():
    """Something cheap to visit to prove the app is actually up.

    Also answers "did my DATABASE_URL really get set on the server?", which you
    cannot check any other way - students are not allowed to run config:show.
    """
    return {"status": "ok", "database": app.config["DATABASE_CONFIGURED"]}, 200


# --- Blueprints -------------------------------------------------------------
# A blueprint is a group of related pages kept in its own file. Register each
# one here. You will add your own in Database + SQL and remove the examples one.
from blueprints.examples import examples_bp  # noqa: E402

app.register_blueprint(examples_bp)


# --- Error pages ------------------------------------------------------------
@app.errorhandler(DatabaseNotConfigured)
def database_not_configured(error):
    """Shown when a page needs a database and none is set up yet.

    This is why no page in blueprints/ has to check whether a database exists:
    they just use it, and if it is not there this handler explains why. Every
    blueprint you write later gets the same behaviour for free.
    """
    return render_template("no_database.html", message=str(error)), 503


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
