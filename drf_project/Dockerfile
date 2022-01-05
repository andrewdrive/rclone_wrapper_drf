FROM python:3.8.10
ENV PYTHONUNBUFFERED=1

RUN mkdir /rest
WORKDIR /rest
COPY requirements.txt /rest/
RUN apt-get update
RUN apt-get install -y --allow-downgrades libsqlite3-0=3.22.0-1
RUN apt-get install -y sqlite3 

ADD ./ /rest/