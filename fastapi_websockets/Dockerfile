FROM python:3.8.10
ENV PYTHONUNBUFFERED=1

RUN mkdir /websockets
WORKDIR /websockets
COPY requirements.txt /websockets/
RUN apt-get update

ADD ./ /websockets/