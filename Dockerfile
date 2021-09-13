FROM python:3.8-slim

RUN apt-get update

RUN mkdir /code
COPY ./requirements.txt /requirements.txt
COPY . /app
WORKDIR /app

RUN python -m venv /py
RUN /py/bin/pip install gunicorn
RUN /py/bin/pip install -r requirements.txt
RUN /py/bin/python3 manage.py migrate
RUN /py/bin/python3 manage.py collectstatic --noinput
RUN mkdir score_files
