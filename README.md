## Real-time, multiplayer card games

### To run the card-games app locally:
* docker-compose build
* docker-compose up
* Cribbage runs at http://localhost:5000
* Pinochle runs at http://localhost:5001

### To run the tests
* docker-compose exec -T cribbage coverage run -m  pytest
* docker-compose exec -T cribbage coverage report
