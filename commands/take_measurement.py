#!/usr/bin/env python3
import click
from flask.cli import with_appcontext


@click.command(help="to measure the internet speed")
@with_appcontext
def take_measurement():
    from repository import SpeedTestRepository
    from database.client import db

    repo = SpeedTestRepository(db)
    raw_data = repo.execute()
    repo.add_item(raw_data)


if __name__ == "__main__":
    take_measurement()
