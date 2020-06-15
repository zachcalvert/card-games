FROM python:3.8.1-slim-buster

COPY ./requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt
COPY . /code

ENV FLASK_DEBUG 1
ENV FLASK_ENV development
ENV FLASK_APP app.py

EXPOSE 5000

ENTRYPOINT [ "flask", "run", "--host=0.0.0.0" ]
