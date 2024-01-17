###############################################################################
#
# Copyright (C) 2024 Tom Kralidis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

###############################################################################

from io import BytesIO
import json
import logging
import os
from pathlib import Path
import tempfile
from urllib.request import urlopen
import zipfile

import click
import yaml

LOGGER = logging.getLogger(__name__)

DISCOVERY_METADATA_ZIP = os.environ['MSC_WIS2NODE_DISCOVERY_METADATA_ZIP']
DATASET_CONFIG = os.environ['MSC_WIS2NODE_DATASET_CONFIG']


def create_datasets_conf() -> None:
    """
    Create dataset definition configuration

    :returns: `None`
    """

    skips = ['other', 'shared', 'template']

    datasets_conf = {
        'datasets': []
    }

    with tempfile.TemporaryDirectory() as td:
        fh = BytesIO(urlopen(DISCOVERY_METADATA_ZIP).read())
        with zipfile.ZipFile(fh) as z:
            z.extractall(td)
            path = Path(td) / 'discovery-metadata-master'
            mcfs_to_process = path.rglob('*.yml')

            for path_object in mcfs_to_process:
                LOGGER.debug(f'Path: {path_object}')
                if any([s in str(path_object) for s in skips]):
                    LOGGER.debug('Skipping')
                    continue

                try:
                    with path_object.open() as fh2:
                        mcf = yaml.load(fh2, Loader=yaml.SafeLoader)

                        dataset = {
                            'metadata_id': mcf['metadata']['identifier']
                        }
                        datasets_conf['datasets'].append(dataset)

                        if mcf['metadata']['identifier'] is None:
                            print("NONE", path_object)

                except yaml.parser.ParserError as err:
                    LOGGER.warning(f'YAML parsing error: {err}')
                    LOGGER.warning('Skipping')
                except (KeyError, TypeError) as err:
                    LOGGER.warning(f'key not defined: {err}')
                except AttributeError as err:
                    LOGGER.warning(f'Missing distribution: {err}')

    with Path(DATASET_CONFIG).open('w') as fh:
        json.dump(datasets_conf, fh, indent=4)


@click.group()
def dataset():
    """Dataset management"""

    pass


@click.command()
@click.pass_context
def setup(ctx):
    """Setup dataset definitions"""

    click.echo('Downloading MSC Discovery Metadata MCF files')

    create_datasets_conf()


dataset.add_command(setup)
