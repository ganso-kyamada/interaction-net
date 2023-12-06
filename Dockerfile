FROM python:3.12

ENV TZ=Asia/Tokyo
RUN apt update && apt-get install -y wget gnupg2 libnss3 wait-for-it bash

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app
