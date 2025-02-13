FROM python:3.7-slim

WORKDIR /app

COPY . /app

COPY requirements.txt requirements.txt  