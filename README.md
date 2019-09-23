# Gerrit Load Testing

This project provides a tool to load test Gerrit by running a set of actions
typically used by Gerrit users.

## Requirements

- Python 3
- Pipenv [1]

## Contribute

The python scripts are formatted using `black` [2]. The code style is further
checked by `pylint` [3].

To install the tools, run:

```sh
pipenv install --dev
```

To lint the files, run:

```sh
pipenv run black $(find . -name '*.py') && pipenv run pylint $(find . -name '*.py')
```

Black will automatically format all python-files. Pylint, however, will not
automatically fix issues in the code. Please fix the issues pylint is showing or
in reasonable cases disable the respective rules in a reasonable scope.

## Build

The tool is meant to be run in a container. To build this container, run:

```sh
docker build -t gerrit/loadtester ./container
```

## Run

### Docker

To run an instance of the load tester. run:

```sh
docker run -it gerrit/loadtester \
  --duration $TEST_DURATION \
  --password $GERRIT_PWD \
  --url $GERRIT_URL \
  --user $GERRIT_USER
```

The options are:

- `--duration` (default: `None`): Duration, for which to run the tests in
  seconds (optional; if not set, test runs until stopped)
- `--password` (default: `secret`): Password of Gerrit user used for executing
  actions
- `--url`: URL of Gerrit (REQUIRED; e.g. `https://gerrit.example.com`)
- `--user` (default: `admin`): User to be used for executing actions

### Kubernetes

The docker containers may be used to run the load tests in Kubernetes to simulate
multiple users (each instance acts as a single user). This project provides an
example deployment yaml: `./load-tester.deployment.yaml`.
Further, an example deployment for a logging stack based on ElasticSearch,
FluentBit and Kibana to collect the logs created by the load testing scripts is
provided in `./efk/`.

## Links

[1] https://github.com/pypa/pipenv
[2] https://github.com/psf/black
[3] https://www.pylint.org/
