import json
import subprocess
import sys
from abc import ABC
from datetime import datetime
from typing import Dict
from typing import Optional

import pytz
from flask_sqlalchemy import SQLAlchemy
from injector import inject
from marshmallow import EXCLUDE
from sqlalchemy import desc
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session

from configuration import BaseConfig
from models import Measurement
from models import Server
from schemas import ResultSchema


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


class SpeedTestRepository(SpeedTestInterface, DatabaseRepository):
    def execute(self):
        result = subprocess.run(self.cmd, capture_output=True)
        if result.returncode != 0:
            print(result.stderr.decode())
            now_datetime = datetime.utcnow().replace(microsecond=0)
            fake_data = {"timestamp": now_datetime.isoformat()}
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
