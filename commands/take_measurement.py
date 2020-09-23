#!/usr/bin/env python3
import click
from flask.cli import with_appcontext


@click.command(help="to measure the internet speed")
@with_appcontext
def take_measurement():
    pass


if __name__ == "__main__":
    take_measurement()
