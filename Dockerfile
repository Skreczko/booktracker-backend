FROM python:3.12

ENV PYTHONUNBUFFERED 1
RUN adduser --disabled-password --gecos '' user

RUN apt-get update && \
    apt-get install -y gettext postgresql-client vim make libpq-dev && \
    apt-get clean
RUN mkdir /code

# RUN pip install -U pip
RUN pip install pip==23.1.2

# Requirements
ADD ./requirements /code/requirements

# For local development
RUN pip install -r /code/requirements/dev.txt

ADD . /code/

WORKDIR /code


