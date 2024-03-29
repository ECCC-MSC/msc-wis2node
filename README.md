[![flake8](https://github.com/ECCC-MSC/msc-wis2node/workflows/flake8/badge.svg)](https://github.com/ECCC-MSC/msc-wis2node/actions)

# msc-wis2node

MSC WMO WIS2 Node implementation

<a href="https://github.com/ECCC-MSC/msc-wis2node/blob/main/docs/architecture/c4-container.png"><img alt="MSC WIS2 Node C4 container diagram" src="https://github.com/ECCC-MSC/msc-wis2node/blob/main/docs/architecture/c4-container.png" width="800"/></a>

For more information, see the [architecture documentation](https://github.com/ECCC-MSC/msc-wis2node/blob/main/docs/architecture)

## Installation

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during msc-wis2node installation.

### Installing msc-wis2node

```bash
# setup virtualenv
python3 -m venv --system-site-packages msc-wis2node
cd msc-wis2node
source bin/activate

# clone codebase and install
git clone https://github.com/ECCC-MSC/msc-wis2node.git
cd msc-wis2node
python3 setup.py install

# install sarracenia configurations
# verify configuration directory (default is based on $HOME/.config/sr3)
make check
# install configurations
make install

# override the configuration default installation location
make install SR3_CONFIG=/path/to/foo
```

## Running

```bash
# setup environment and configuration
cp msc-wis2node.env local.env
vim local.env  # update accordingly
#
# environment variables
#
# MSC_WIS2NODE_BROKER_HOSTNAME: hostname of the MQTT broker to publish to
# MSC_WIS2NODE_BROKER_PORT: port of the MQTT broker to publish to
# MSC_WIS2NODE_BROKER_USERNAME: username of the MQTT broker to publish to=admin
# MSC_WIS2NODE_BROKER_PASSWORD: password of the MQTT broker to publish to
# MSC_WIS2NODE_MSC_DATAMART_AMQP: URL to MSC Datamart notification service
# MSC_WIS2NODE_DATASET_CONFIG: filepath where MSC dataset definitions are managed
# MSC_WIS2NODE_DISCOVERY_METADATA_ZIP_URL: URL to SSC GitLab zipfile of MSC discovery metadata
# MSC_WIS2NODE_TOPIC_PREFIX: base topic prefix for publication (i.e. origin/a/wis2/ca-eccc-msc)

source local.env

# setup dataset configuration based on zipfile defined in $MSC_WIS2NODE_DISCOVERY_METADATA_ZIP_URL
# note: $MSC_WIS2NODE_DISCOVERY_METADATA_ZIP_URL can be overridden with the --metadata-zipfile option
# on the command line
#
# the output is written to $MSC_WIS2NODE_DATASET_CONFIG by default, and can be overriden with the --output
# option on the command line

msc-wis2node dataset setup

# connect to MSC Datamart notification service
sr3 start subscribe/dd.weather.gc.ca-all
```

### Docker

Instructions to run msc-wis2node via Docker can be found in the [`docker`](docker) directory.

## Development

### Running Tests

```bash
# install dev requirements
pip3 install -r requirements-dev.txt

# run tests like this:
python3 tests/run_tests.py

# or this:
python3 setup.py test
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/ECCC-MSC/msc-wis2node/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
