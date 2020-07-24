## Real-time, multiplayer card games

### To run the card-games app locally:
* docker-compose build
* docker-compose up
* cribbage runs at http://localhost:5000
* pinochle runs at http://localhost:5001 (WIP)

### To run the tests
* docker-compose exec -T cribbage coverage run -m  pytest
* docker-compose exec -T cribbage coverage report
