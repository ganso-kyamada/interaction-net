FROM python:3.9

WORKDIR /app

RUN apt update && apt install -y \
  wait-for-it bash
COPY . .
RUN pip install -r requirements.txt
