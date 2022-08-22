FROM python:3.10-slim-buster

RUN useradd doctorly

RUN mkdir -p /home/doctorly/docterlyapi
WORKDIR /home/doctorly/docterlyapi

# COPY . /home/doctorly/docterlyapi/
COPY api api
COPY migrations migrations
COPY app.py app.py
COPY requirements.txt requirements.txt
COPY db_dump db_dump
COPY logs logs
COPY secrets.json /etc/

RUN python -m venv venv 
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN venv/bin/pip install -r requirements.txt
ENV FLASK_APP=app.py\
    FLASK_ENV=development
RUN venv/bin/flask db upgrade
EXPOSE 5000
CMD ["venv/bin/flask", "run", "--host=0.0.0.0"]