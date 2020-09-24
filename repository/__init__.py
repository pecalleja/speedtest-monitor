import json
import subprocess
import sys
from abc import ABC
from datetime import datetime
from typing import Dict
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from marshmallow import EXCLUDE
from marshmallow import fields
from marshmallow import pre_load
from marshmallow import Schema
from sqlalchemy import desc
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session

from configuration import BaseConfig
from models import Measurement
from models import Server


class DatabaseRepository(ABC):
    db_session: Session

    @inject
    def __init__(self, db: SQLAlchemy):
        self.db_session = db.session

    def add_item(self, data: Dict) -> Measurement:
        raise NotImplementedError

    def list_items(self, filters: Optional[Dict] = None) -> Query:
        raise NotImplementedError


class SpeedTestInterface(ABC):
    cmd = BaseConfig.COMMAND

    def execute(self) -> dict:
        raise NotImplementedError


class ResultSchema(Schema):
    uuid = fields.String(allow_none=True)
    download = fields.Float(allow_none=True)
    upload = fields.Float(allow_none=True)
    latency = fields.Float(allow_none=True)
    isp = fields.String(allow_none=True)
    server = fields.Dict(allow_none=True)
    created_at = fields.DateTime(required=True)

    @pre_load
    def convert_mapping(self, data, **kwargs):
        raw_download = data.get("download", {}).get("bandwidth", 0)
        raw_upload = data.get("upload", {}).get("bandwidth", 0)
        new_data = {
            "uuid": data.get("result", {}).get("id"),
            "download": raw_download / BaseConfig.SPEEDFACTOR,
            "upload": raw_upload / BaseConfig.SPEEDFACTOR,
            "latency": data.get("ping", {}).get("latency", 0),
            "isp": data.get("isp"),
            "server": data.get("server", {}),
            "created_at": data.get("timestamp"),
        }
        return new_data


class SpeedTestRepository(SpeedTestInterface, DatabaseRepository):
    def execute(self):
        result = subprocess.run(self.cmd, capture_output=True)
        if result.returncode != 0:
            print(result.stderr.decode(), file=sys.stderr)
            fake_data = {
                "timestamp": datetime.now(tz=BaseConfig.TIMEZONE).isoformat()
            }
            return fake_data

        data = json.loads(result.stdout.decode())
        return data

    def add_item(self, data: dict):
        new_data = ResultSchema(unknown=EXCLUDE).load(data)
        server_id = new_data.get("server").get("id")
        server = None
        if server_id:
            server = (
                self.db_session.query(Server)
                .filter(Server.id == server_id)
                .one_or_none()
            )

        if server_id and not server:
            server_data = new_data.pop("server")
            server = Server(**server_data)
            self.db_session.add(server)

        new_data["server"] = server
        new_obj = Measurement(**new_data)
        self.db_session.add(new_obj)
        self.db_session.commit()
        return new_obj

    def list_items(self, filters: Optional[Dict] = None) -> Query:
        return self.db_session.query(Measurement).order_by(
            desc(Measurement.created_at)
        )
