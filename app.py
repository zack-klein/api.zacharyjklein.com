import logging
import os

from flask import Flask
from flask_cors import CORS

from flask_restplus import Api

from database import db
from apis import (
    legacy,
    keyme,
    corona,
    resumayday,
    sentimenter,
    healthy,
    pollin,
    whatsmybill,
    zacks_todos,
    openaq,
    nurse,
)


# SQLAlchemy setup
DEFAULT_SQLALCHEMY_CONN = "sqlite:///sample_db.sqlite"
SQLALCHEMY_CONN = os.environ.get(
    "SQLALCHEMY_CONN_STRING", DEFAULT_SQLALCHEMY_CONN
)
TABLE_NAME = "todos"

if SQLALCHEMY_CONN == DEFAULT_SQLALCHEMY_CONN:
    logging.warning(
        f"No SQLAlchemy conn string here! Using {DEFAULT_SQLALCHEMY_CONN}"
    )

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_CONN
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    try:
        db.create_all()

    except Exception as e:
        logging.warning(f"Tried to create the db but failed with error: {e}")


CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

api.add_namespace(legacy.api)
api.add_namespace(keyme.api)
api.add_namespace(corona.api)
api.add_namespace(resumayday.api)
api.add_namespace(sentimenter.api)
api.add_namespace(healthy.api)
api.add_namespace(pollin.api)
api.add_namespace(whatsmybill.api)
api.add_namespace(zacks_todos.api)
api.add_namespace(openaq.api)
api.add_namespace(nurse.api)
