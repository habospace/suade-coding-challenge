FROM python:3.10-slim

RUN apt-get update
RUN apt-get -y install cmake g++
RUN apt-get -y install libpq-dev
RUN pip install --upgrade pip

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install gunicorn

COPY ./app/web_api/ /app/web_api/
COPY ./app/data_repositories/ /app/data_repositories/

