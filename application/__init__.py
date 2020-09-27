from http import HTTPStatus

from flask import Blueprint
from flask import render_template
from flask import request
from injector import inject

from repository import SpeedTestRepository
from schemas import ResultSchema


app_blueprint = Blueprint(
    "api", __name__, static_folder="static", static_url_path="/static"
)


@inject
@app_blueprint.route("/measurement", methods=("GET",))
def measurement(repository: SpeedTestRepository):
    params = dict(request.args)
    result = repository.list_items(params)
    return {
        "result": ResultSchema(
            many=True, only=("created_at", "upload", "download", "latency")
        ).dump(result)
    }


@app_blueprint.route("/", methods=("GET",))
def graph():
    return render_template("graph.html")
