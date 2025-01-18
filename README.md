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
cd msc-wis2node/msc-wis2node-management
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
# MSC_WIS2NODE_DISCOVERY_METADATA_ZIP: zipfile of MSC discovery metadata (file or URL)
# MSC_WIS2NODE_TOPIC_PREFIX: base topic prefix for publication (i.e. origin/a/wis2/ca-eccc-msc)
# MSC_WIS2NODE_CACHE: optional memcache instance
# MSC_WIS2NODE_CACHE_EXPIRY_SECONDS: number of seconds for cache items to expire (default 86400 [1 day])
# MSC_WIS2NODE_CENTRE_ID: centre identifier
# MSC_WIS2NODE_WIS2_GDC: URL to a WIS2 GDC (default is Canada GDC)

source local.env

# setup dataset configuration based on zipfile defined in $MSC_WIS2NODE_DISCOVERY_METADATA_ZIP
# note: $MSC_WIS2NODE_DISCOVERY_METADATA_ZIP can be overridden with the --metadata-zipfile option
# on the command line
#
# the output is written to $MSC_WIS2NODE_DATASET_CONFIG by default, and can be overriden with the --output
# option on the command line

msc-wis2node dataset setup

# connect to MSC Datamart notification service
sr3 start subscribe/dd.weather.gc.ca-all

# delete metadata records

msc-wis2node dataset delete-metadata --metadata-id 12345
```

### Docker

The Docker setup uses Docker and Docker Compose to manage the following services:

- **msc-wis2node-cache**: memcache caching for data update detection (optional)
- **msc-wis2node-management**: management service to subscribe to MSC Datamart/HPFX and re-publish to WIS2

See [`msc-wis2node.env`](msc-wis2node.env) for default environment variable settings.

To adjust service ports, edit [`docker-compose.override.yml`](docker-compose.override.yml) accordingly.

The [`Makefile`](Makefile) in the root directory provides options to manage the Docker Compose setup.

```bash
# build all images
make build

# build all images (no cache)
make force-build

# start all containers
make up

# start all containers in dev mode
make dev

# view all container logs in realtime
make logs

# login to the msc-wis2node-management container
make login

# restart all containers
make restart

# shutdown all containers
make down

# remove all volumes
make rm
```


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
