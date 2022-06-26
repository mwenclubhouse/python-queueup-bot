# syntax=docker/dockerfile:1
# https://docs.docker.com/language/python/build-images/
FROM python:3.8-slim-buster
WORKDIR /app

RUN apt update
RUN apt upgrade -y
RUN apt install gcc -y
COPY requirements.txt requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]