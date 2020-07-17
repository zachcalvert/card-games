FROM python:3.8.1-slim-buster

COPY ./requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt
COPY . /code

ENV FLASK_DEBUG 1
ENV FLASK_ENV development

EXPOSE 5001

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5001", "--access-logfile", "-", "--worker-class", "eventlet", "-w", "1", "app:pinochle"]