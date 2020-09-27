from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Query


class FilterInterface:
    start: datetime
    end: datetime

    def __init__(self, schema):
        self.schema = schema

    def load_data(self, data: Dict):
        raise NotImplementedError

    def apply(self, query: Query):
        raise NotImplementedError


class MeasureFilter(FilterInterface):
    def load_data(self, data: Dict):
        valid_filters = self.schema.load(data)
        self.start = valid_filters.get("start")
        self.end = valid_filters.get("end")

    def apply(self, query: Query):
        from models import Measurement

        if self.start:
            query = query.filter(Measurement.created_at >= self.start)
        if self.end:
            query = query.filter(Measurement.created_at <= self.end)
        return query
