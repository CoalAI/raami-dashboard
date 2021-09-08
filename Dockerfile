FROM python:3.8-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN mkdir /code
COPY ./requirements.txt /requirements.txt
COPY . /app
WORKDIR /app

RUN python -m venv /py
RUN /py/bin/pip install gunicorn
RUN /py/bin/pip install -r requirements.txt
RUN /py/bin/python3 manage.py migrate
RUN /py/bin/python3 manage.py collectstatic --noinput
RUN adduser --disabled-password --no-create-home django-user

ENV PATH="/py/bin:$PATH"

USER django-user

CMD gunicorn --bind 0.0.0.0:8006 --workers 1 --threads 8 --timeout 0 raamiDashboard.wsgi
