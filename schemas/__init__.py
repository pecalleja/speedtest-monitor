from datetime import datetime

import pytz
from delorean import Delorean
from delorean import parse as datetime_parse
from marshmallow import fields
from marshmallow import pre_load
from marshmallow import Schema

from configuration import BaseConfig


class CustomDateTimeField(fields.DateTime):
    timezone = "UTC"

    @staticmethod
    def _convert_to_timezone(del_obj: Delorean) -> datetime:
        timezone = pytz.timezone(BaseConfig.TIMEZONE)
        if del_obj.datetime.tzinfo != timezone:
            dt = del_obj.shift(BaseConfig.TIMEZONE).truncate("second").datetime
        else:
            dt = del_obj.truncate("second").datetime
        return dt

    def _serialize(self, value, attr, obj, **kwargs):
        del_obj = Delorean(value, timezone=BaseConfig.TIMEZONE)
        return self._convert_to_timezone(del_obj).isoformat()

    def _deserialize(self, value, attr, data, **kwargs):
        del_obj = datetime_parse(value, dayfirst=False, timezone=self.timezone)
        return self._convert_to_timezone(del_obj)


class ResultSchema(Schema):
    uuid = fields.String(allow_none=True)
    download = fields.Float(allow_none=True)
    upload = fields.Float(allow_none=True)
    latency = fields.Float(allow_none=True)
    isp = fields.String(allow_none=True)
    server = fields.Dict(allow_none=True)
    created_at = CustomDateTimeField(required=True)

    @pre_load
    def convert_mapping(self, data, **kwargs):
        raw_download = data.get("download", {}).get("bandwidth", 0)
        raw_upload = data.get("upload", {}).get("bandwidth", 0)
        new_data = {
            "uuid": data.get("result", {}).get("id"),
            "download": round(raw_download / BaseConfig.SPEEDFACTOR, 2),
            "upload": round(raw_upload / BaseConfig.SPEEDFACTOR, 2),
            "latency": data.get("ping", {}).get("latency", 0),
            "isp": data.get("isp"),
            "server": data.get("server", {}),
            "created_at": data.get("timestamp"),
        }
        return new_data


class FilterDatetime(CustomDateTimeField):
    timezone = BaseConfig.TIMEZONE


class FilterSchema(Schema):
    start = FilterDatetime()
    end = FilterDatetime()
