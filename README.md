# Gerrit Load Testing

This project provides a tool to load test Gerrit by running a set of actions
typically used by Gerrit users.

The test relies heavily on randomness. The script will for the duration of the
tests loop through all possible actions that are defined. For each action it will
calculate a random number between 0 and 1 and execute the action if the number
is higher than a configured threshold. Thus, depending on the configuration, not
all actions will be executed in each cycle of the loop, thereby simulating that
users will not always do the same series of actions. By adjusting the probability
thresholds different scenarios based on statistics can be simulated.

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

## Configuration

A configuration file in yaml-format can be used to configure the test run. The
`config.sample.yaml`-file gives an example-configuration.

The single configuration values are listed here:

| key                                             | description                                                                           | default value           |
|-------------------------------------------------|---------------------------------------------------------------------------------------|-------------------------|
| `gerrit.url`                                    | URL of the Gerrit test server                                                         | `http://localhost:8080` |
| `gerrit.user`                                   | Gerrit user used for tests                                                            | `admin`                 |
| `gerrit.password`                               | Password of Gerrit user                                                               | `secret`                |
| `testrun.duration`                              | Duration for which to run the tests                                                   | `null` (indefinitely)   |
| `testrun.initialization.delay.enabled`          | Whether to delay execution of a test run                                              | `true`                  |
| `testrun.initialization.delay.min`              | Minimum initial delay in seconds                                                      | `0`                     |
| `testrun.initialization.delay.max`              | Maximum initial delay in seconds                                                      | `300`                   |
| `testrun.initialization.createProjects.enabled` | Whether to create new projects during initialization                                  | `true`                  |
| `testrun.initialization.createProjects.number`  | How many new projects to create during initialization                                 | `1`                     |
| `testrun.initialization.knownProjects`          | List of projects that the simulated user knows of from the beginning                  | `nil`                   |
| `testrun.waitBetweenCycles.enabled`             | Whether to pause between test cycles                                                  | `true`                  |
| `testrun.waitBetweenCycles.min`                 | Minimum time of pause                                                                 | `1`                     |
| `testrun.waitBetweenCycles.max`                 | Maximum time of pause                                                                 | `10`                    |
| `actions.*`                                     | Probability with which an action is performed in each cycle (`0`: never, `1`: always) | `1`                     |

### Available actions

The following actions can be performed by the tests:

| key                          | description                                                                              |
|------------------------------|------------------------------------------------------------------------------------------|
| `clone_project`              | Test performs a clone of a project, that is assigned to the simulated user               |
| `create_project`             | Test creates a new project via REST                                                      |
| `fetch_project`              | Test fetches a project, that is assigned to the simulated user and was already cloned    |
| `push_for_review`            | Test creates random commits in a cloned project and pushes them to `refs/for/master`     |
| `push_head_to_master`        | Test creates random commits in a cloned project and pushes them to the remote's `master` |
| `query_hundred_open_changes` | Queries changes via REST                                                                 |
| `query_projects`             | Queries projects via REST                                                                |
| `review_change`              | Reviews a change via REST                                                                |

## Run

### Docker

To run an instance of the load tester. run:

```sh
docker run -it gerrit/loadtester \
  --config $CONFIG_FILE \
  --duration $TEST_DURATION \
  --password $GERRIT_PWD \
  --url $GERRIT_URL \
  --user $GERRIT_USER
```

The options are:

- `--config` (default: `None`): Path to a config file (optional). The config file
  has to be present in the container, either by building it in or by mounting it.
  Parameters will overwrite configuration from file.
- `--duration` (default: `None`): Duration, for which to run the tests in
  seconds (optional; if not set, test runs until stopped)
- `--password` (default: `secret`): Password of Gerrit user used for executing
  actions
- `--url`: URL of Gerrit (REQUIRED; e.g. `https://gerrit.example.com`)
- `--user` (default: `admin`): User to be used for executing actions

If the target Gerrit server is using the HTTPS-protocol, the load test requires
a valid not self-signed CA. Certificates that are mounted to the
`/var/loadtest/certs` will be used to that perpose. This can be done like this:

```sh
docker run -it gerrit/loadtester \
  -v <certificate dir>:/var/loadtest/certs
```

### Kubernetes

The docker containers may be used to run the load tests in Kubernetes to simulate
multiple users (each instance acts as a single user). This project provides an
example deployment yaml: `./kubernetes/load-tester/load-tester.*.yaml`.
To install the Kubernetes setup, adjust the configuration in the yaml-files.

- Configure the Gerrit user data and add certificates for HTTPS-connections
  in `./kubernetes/load-tester/load-tester.secret.yaml`.
  The values have to be base64-encoded.
- Adjust the configuration file in `./kubernetes/load-tester/load-tester.configmap.yaml`.
  The config-file structure is the same as described above.
- Adjust the number of replica-pods and the location of the docker image in
  `./kubernetes/load-tester/load-tester.deployment.yaml`.

Afterwards, create all resources on the cluster:

```sh
Kubectl apply ./kubernetes/load-tester/load-tester.secret.yaml
Kubectl apply ./kubernetes/load-tester/load-tester.configmap.yaml
Kubectl apply ./kubernetes/load-tester/load-tester.deployment.yaml
```

Further, an example deployment for a logging stack based on ElasticSearch,
FluentBit and Kibana to collect the logs created by the load testing scripts is
provided in `./efk/`.

To install the EFK-stack, run:

```sh
helm install stable/elasticsearch \
  -n elasticsearch \
  -f ./kubernetes/efk/elasticsearch.yaml \
  --namespace logging

helm install stable/fluent-bit \
  -n fluentbit \
  -f ./kubernetes/efk/fluentbit.yaml \
  --namespace logging

helm install stable/kibana \
  -f kubernetes/efk/kibana.yaml \
  -n kibana \
  --namespace logging
```

## Links

[1] https://github.com/pypa/pipenv
[2] https://github.com/psf/black
[3] https://www.pylint.org/
