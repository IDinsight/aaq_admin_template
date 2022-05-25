"""
Create and initialise the app. Uses Blueprints to define views
"""
import os

from flask import Flask
from flask_bootstrap import Bootstrap

from .database_sqlalchemy import db
from .utils import DefaultEnvDict, get_postgres_uri

bootstrap = Bootstrap()


def create_app(params=None, enable_ud=False):
    """
    Factory to create a new flask app instance
    """
    app = Flask(__name__)
    setup(app, params, enable_ud)
    from .db_ui import db_ui as dbui_blueprint
    from .demo_ui import demo_ui as demo_blueprint
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(dbui_blueprint)
    app.register_blueprint(demo_blueprint)

    if enable_ud:
        from .ud_ui import ud_ui as ud_blueprint

        app.register_blueprint(ud_blueprint)

    return app


def setup(app, params, enable_ud):
    """
    Add config to app and initialise extensions.

    Parameters
    ----------
    app : Flask app
        A newly created flask app
    params : Dict
        A dictionary with config parameters
    """

    if params is None:
        params = {}
    config = get_config_data(params)
    setup_core(app, config)

    if enable_ud:
        setup_ud(app, config)

    bootstrap.init_app(app)
    db.init_app(app)


def setup_core(app, config):
    """
    Setup config parameters for core admin app i.e. Dbui and Demo
    """
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_pre_ping": True,
            "pool_recycle": 300,
        },
        **config
    )

    app.MODEL_PROTOCOL = config["MODEL_PROTOCOL"]
    app.MODEL_HOST = config["MODEL_HOST"]
    app.MODEL_PORT = config["MODEL_PORT"]
    app.INBOUND_CHECK_TOKEN = config["INBOUND_CHECK_TOKEN"]


def setup_ud(app, config):
    """
    Setup config parameters for Urgency Detection
    """
    app.UD_PROTOCOL = config["UD_PROTOCOL"]
    app.UD_HOST = config["UD_HOST"]
    app.UD_PORT = config["UD_PORT"]
    app.UD_INBOUND_CHECK_TOKEN = config["UD_INBOUND_CHECK_TOKEN"]
    app.config["UD_ENABLED"] = True


def get_config_data(params):
    """
    If parameter exists in `params` use that else use env variables.
    """

    config = DefaultEnvDict()
    config.update(params)

    config["SQLALCHEMY_DATABASE_URI"] = get_postgres_uri(
        config["PG_ENDPOINT"],
        config["PG_PORT"],
        config["PG_DATABASE"],
        config["PG_USERNAME"],
        config["PG_PASSWORD"],
    )

    return config
