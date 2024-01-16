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
```

## Running

```bash
# setup environment and configuration
cp msc-wis2node.env local.env
vim local.env # update accordingly

source local.env

# setup msc-wis2node
msc-wis2node setup

# connect to MSC Datamart notification service
sr3 start subscribe/msc-wis2node
```

### Docker

Instructions to run msc-wis2node via Docker can be found the [`docker`](docker) directory.

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
