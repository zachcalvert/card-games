from flask.cli import FlaskGroup

from app import pinochle


cli = FlaskGroup(pinochle)


@cli.command("populate_redis")
def populate_redis():
    pass


if __name__ == "__main__":
    cli()
