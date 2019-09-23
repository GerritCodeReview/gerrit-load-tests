FROM python:3.7-alpine

WORKDIR /usr/src/app

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apk --no-cache --update-cache add git gcc gfortran build-base

COPY dependencies/ ./

RUN pip3 install --no-cache --upgrade pipenv && \
    pipenv install --python 3.7.3 --system

COPY tools/ ./

ENTRYPOINT [ "python3", "./start_test.py" ]
