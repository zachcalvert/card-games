## Real-time, multiplayer cribbage
![gameplay screenshot](https://i.imgur.com/7RD8J4p.png)

### To run cribbage.live locally:
* docker-compose up --build
* app runs at http://localhost:5000

### To run the tests
* docker-compose exec -T flask coverage run -m  pytest
* docker-compose exec -T flask coverage report
