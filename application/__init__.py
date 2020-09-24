from http import HTTPStatus

from flask import Blueprint
from flask import request
from injector import inject

from repository import SpeedTestRepository
from schemas import ResultSchema


app_blueprint = Blueprint(
    "api", __name__, static_folder=None, static_url_path=None
)


@inject
@app_blueprint.route("/", methods=("GET",))
def main(repository: SpeedTestRepository):
    result = repository.list_items()
    return {
        "result": ResultSchema(
            many=True, only=("created_at", "upload", "download", "latency")
        ).dump(result)
    }
