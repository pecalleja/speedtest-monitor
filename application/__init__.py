from http import HTTPStatus

from flask import Blueprint
from flask import request
from injector import inject


app_blueprint = Blueprint(
    "api", __name__, static_folder=None, static_url_path=None
)


@inject
@app_blueprint.route("/", methods=("GET",))
def main():
    return "Hello World !"
