FROM python:3.10-slim

RUN pip install --upgrade pip

WORKDIR /app

COPY Pipfile Pipfile.lock /app/

RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install gunicorn

COPY ./data/ /data/
COPY ./app/web_api/ /app/web_api/
COPY ./app/data_repositories/ /app/data_repositories/
