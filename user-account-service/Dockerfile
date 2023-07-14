FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app/

ENV PYTHONUNBUFFERED=1

RUN chmod +x server.sh 



