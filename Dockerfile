FROM python:3.12

ENV TZ=Asia/Tokyo
RUN apt update && apt-get install -y wget gnupg2 libnss3 wait-for-it bash

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
