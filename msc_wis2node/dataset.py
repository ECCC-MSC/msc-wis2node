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
import logging
from pathlib import Path
import tempfile
from typing import Union
from urllib.request import urlopen
import zipfile

import click
import yaml

from msc_wis2node import cli_options
from msc_wis2node.env import DATASET_CONFIG, DISCOVERY_METADATA_ZIP_URL

LOGGER = logging.getLogger(__name__)


FORMATS = {
    'GRIB2': 'application/x-grib',
    'BUFR': 'application/x-bufr'
}


def create_datasets_conf(metadata_zipfile: Union[Path, None],
                         output: Path) -> None:
    """
    Create dataset definition configuration

    :param metadata_zipfile: path to zipfile of MCF repository
    :param output: `Path` object of output file

    :returns: `None`
    """

    skips = ['other', 'shared', 'template']

    datasets_conf = {
        'datasets': []
    }

    if metadata_zipfile is not None:
        with metadata_zipfile.open('rb') as fh:
            zipfile_content = fh.read()
    else:
        zipfile_content = urlopen(DISCOVERY_METADATA_ZIP_URL).read()

    with tempfile.TemporaryDirectory() as td:
        fh = BytesIO(zipfile_content)
        with zipfile.ZipFile(fh) as z:
            LOGGER.debug(f'Extracting all MCFs to {td}')
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
                            'metadata-id': mcf['metadata']['identifier']
                        }
                        datasets_conf['datasets'].append(dataset)

                        if mcf['metadata'].get('identifier') is None:
                            msg = f'No metadata identifier in {path_object}'
                            LOGGER.error(msg)

                        dataset['subtopic'] = mcf['distribution']['amqps_eng-CAN']['url'].split('/')[-1]  # noqa
                        dataset['wis2-topic'] = mcf['distribution']['mqtt_eng-CAN']['channel']  # noqa

                        format_ = FORMATS[mcf['distribution']['amqps_eng-CAN']['format']['en']]  # noqa
                        dataset['media-type'] = format_
                except yaml.parser.ParserError as err:
                    LOGGER.warning(f'YAML parsing error: {err}')
                    LOGGER.warning('Skipping')
                except (KeyError, TypeError) as err:
                    LOGGER.warning(f'key not defined: {err}')
                except AttributeError as err:
                    LOGGER.warning(f'Missing distribution: {err}')

    LOGGER.debug(f'Dumping YAML document to {output}')
    with output.open('wb') as fh:
        yaml.dump(datasets_conf, fh, sort_keys=False, encoding='utf8',
                  indent=4, default_flow_style=False)


@click.group()
def dataset():
    """Dataset management"""

    pass


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
@cli_options.OPTION_OUTPUT
@click.option('--metadata-zipfile', '-mz',
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='Zipfile of discovery metadata repository')
def setup(ctx, metadata_zipfile, output, verbosity):
    """Setup dataset definitions"""

    click.echo('Setting up runtime dataset definition configuration')

    create_datasets_conf(metadata_zipfile, Path(output or DATASET_CONFIG))


dataset.add_command(setup)
