FROM python:3.7-alpine

WORKDIR /usr/src/app

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apk --no-cache --update-cache add git gcc gfortran build-base

COPY dependencies/ ./

RUN pip3 install --no-cache --upgrade pipenv && \
    pipenv install --python 3.7 --system

COPY tools/ ./

RUN adduser -D loadtest -u 1000 -G users && \
    chown -R 1000:100 /usr/src/app && \
    mkdir -p /var/logs && \
    mkdir -p /var/loadtest && \
    chown -R 1000:100 /var/logs && \
    chown -R 1000:100 /var/loadtest
USER loadtest

RUN git config --global http.sslCAInfo /var/loadtest/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/var/loadtest/ca-certificates.crt

ENTRYPOINT [ "./start.sh" ]
