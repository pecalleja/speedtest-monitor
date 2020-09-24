import json

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TypeDecorator
from sqlalchemy import types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Json(TypeDecorator):
    @property
    def python_type(self):
        return object

    impl = types.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_literal_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return None


class Server(Base):
    __tablename__ = "server"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    country = Column(String)
    host = Column(String)
    port = Column(Integer)
    ip = Column(String)


class Measurement(Base):
    __tablename__ = "measurement"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String)
    download = Column(Float)
    upload = Column(Float)
    latency = Column(Float)
    isp = Column(String)
    server_id = Column(
        ForeignKey("server.id", ondelete="CASCADE"), nullable=True, index=True,
    )
    created_at = Column(DateTime, nullable=False)
    server = relationship("Server", backref="measurements")
