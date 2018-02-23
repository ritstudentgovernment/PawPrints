FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

RUN apk update && \
  apk add postgresql-libs gcc && \
  apk add musl-dev postgresql-dev libxslt-dev libxml2-dev pkgconfig xmlsec-dev


RUN mkdir /PawPrints

WORKDIR /PawPrints

ADD ./requirements.txt /PawPrints/requirements.txt
RUN pip install -r requirements.txt

ADD . /PawPrints
