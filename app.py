import os

from flask import Flask
from flask_injector import FlaskInjector

from application import app_blueprint
from bootstrap import configure
from commands import take_measurement


def create_app():
    flask_app = Flask(__name__, static_folder=None, static_url_path=None)
    flask_app.url_map.strict_slashes = False

    # App configuration
    config = os.getenv("FLASK_CONFIG", "configuration.BaseConfig")
    flask_app.config.from_object(config)

    flask_app.register_blueprint(app_blueprint)
    flask_app.cli.add_command(take_measurement)
    flask_app.app_context().push()
    FlaskInjector(app=flask_app, modules=[configure])
    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)
