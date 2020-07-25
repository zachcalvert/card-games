## Real-time, multiplayer cribbage

### To run cribbage locally:
* docker-compose build
* docker-compose up
* app runs at http://localhost:5000

### To run the tests
* docker-compose exec -T cribbage coverage run -m  pytest
* docker-compose exec -T cribbage coverage report
