FROM --platform=linux/amd64 python:3.13.1-slim

ENV TZ=Asia/Tokyo

RUN apt update && apt-get install -y \
  wget gnupg2 libnss3 wait-for-it bash \
  libgconf-2-4 libgtk-3-0 libxss1 libasound2 libgbm1 libgdk-pixbuf2.0-0 \
  libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libatk1.0-0 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app
