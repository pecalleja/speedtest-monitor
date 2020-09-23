from flask import Flask
from flask_injector import request
from flask_sqlalchemy import SQLAlchemy
from injector import singleton


def configure(binder):
    from database.client import db

    app = binder.injector.get(Flask)
    db.init_app(app)
    binder.bind(Flask, to=app, scope=singleton)
    binder.bind(SQLAlchemy, to=db, scope=singleton)
