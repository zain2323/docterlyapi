FROM python:3.10-slim-buster

RUN useradd doctorly

RUN mkdir -p /home/doctorly/docterlyapi
WORKDIR /home/doctorly/docterlyapi

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the project files
COPY . . 

RUN python -m venv venv 
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN venv/bin/pip install -r requirements.txt
ENV FLASK_APP=app.py\
    FLASK_ENV=development
EXPOSE 5000
CMD ["venv/bin/flask", "run", "--host=0.0.0.0"]
