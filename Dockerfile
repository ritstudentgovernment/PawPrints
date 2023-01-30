FROM python:3.10.9-alpine3.17
ENV PYTHONUNBUFFERED 1

RUN apk update 
RUN apk add postgresql-libs gcc
RUN apk add musl-dev postgresql-client postgresql-dev libxslt-dev libxml2-dev pkgconfig xmlsec-dev

RUN pip install -U pip

RUN mkdir /PawPrints

WORKDIR /PawPrints

ADD ./requirements.txt /PawPrints/requirements.txt
RUN pip install -r requirements.txt

ADD . /PawPrints
