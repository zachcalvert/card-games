### To run the cribbage server locally:
* docker-compose build
* docker-compose up

### To run the tests
* docker-compose run --rm web pytest

### To launch a shell
* docker-compose run --rm web python manage.py shell

Built with a lot of help from: https://flask-socketio.readthedocs.io/en/latest/
