FROM tiangolo/uwsgi-nginx-flask:python3.8.10

WORKDIR /app

COPY . ./