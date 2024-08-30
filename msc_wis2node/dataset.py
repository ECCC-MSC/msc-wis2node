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
    'BUFR': 'application/bufr',
    'CSV': 'text/csv',
    'GRIB2': 'application/grib',
    'GeoJSON': 'application/geo+json',
    'JSON': 'application/json',
    'TXT': 'text/plain',
    'XML': 'application/xml'
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

            path = Path(td)
            mcfs_to_process = path.rglob('mcf/**/*.yml')

            for path_object in mcfs_to_process:
                LOGGER.debug(f'Path: {path_object}')
                if any([s in str(path_object) for s in skips]):
                    LOGGER.debug('Skipping')
                    continue

                try:
                    with path_object.open() as fh2:
                        LOGGER.debug(f'Processing {path_object}')
                        mcf = yaml.load(fh2, Loader=yaml.SafeLoader)

                        if mcf['msc-metadata']['status'] not in ['completed', 'published']:  # noqa
                            LOGGER.info('Metadata not completed or published')
                            continue

                        dataset = {
                            'metadata-id': mcf['metadata']['identifier'],
                            'regexes': []
                        }

                        if mcf['metadata'].get('identifier') is None:
                            msg = f'No metadata identifier in {path_object}'
                            LOGGER.error(msg)

                        dataset['title'] = mcf['identification']['title']['en']
                        dataset['subtopic'] = mcf['distribution']['amqps_eng-CAN']['channel']  # noqa
                        dataset['wis2-topic'] = mcf['distribution']['mqtt_eng-CAN']['channel']  # noqa
                        dataset['media-type'] = get_format(mcf['distribution'])

                        LOGGER.debug('Handling regular expressions')
                        try:
                            for regex in mcf['distribution']['amqps_eng-CAN']['msc-regex-filters']:  # noqa
                                dataset['regexes'].append(regex)
                        except KeyError:
                            pass

                        LOGGER.debug('Handling caching')
                        try:
                            dataset['cache'] = mcf['msc-metadata']['publish-to']['wmo-wis2'].get('cache', True)  # noqa
                        except KeyError:
                            pass

                        datasets_conf['datasets'].append(dataset)

                except (yaml.parser.ParserError, yaml.scanner.ScannerError) as err:  # noqa
                    LOGGER.warning(f'{path_object.name} YAML parsing error: {err}')  # noqa
                    LOGGER.warning('Skipping')
                except (KeyError, TypeError) as err:
                    LOGGER.warning(f'{path_object.name} key not defined: {err}')  # noqa
                except AttributeError as err:
                    LOGGER.warning(f'{path_object.name} missing distribution: {err}')  # noqa

    LOGGER.debug(f'Dumping YAML document to {output}')
    with output.open('wb') as fh:
        yaml.dump(datasets_conf, fh, sort_keys=False, encoding='utf8',
                  indent=4, default_flow_style=False)


def get_format(distribution: dict) -> Union[str, None]:
    """
    Derives format of dataset

    :param distribution: `dict` of distribution objects

    :returns: `str` of format media type if found,
              else default to `application/octet-stream`
    """

    format_ = 'application/octet-stream'

    for key, value in distribution.items():
        if 'format' in value:
            format_ = FORMATS[value['format']['en']]
            LOGGER.debug('Found format {format_}')
            break

    return format_


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
