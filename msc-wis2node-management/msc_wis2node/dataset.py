###############################################################################
#
# Copyright (C) 2026 Tom Kralidis
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
from pathlib import Path
import tempfile
from typing import Union
from urllib.request import urlopen
import uuid
import zipfile

import click
from paho.mqtt import publish
from pygeometa.core import read_mcf
from pywis_pubsub.publish import create_message, get_url_info
import yaml

from msc_wis2node import cli_options
from msc_wis2node.env import (BROKER_HOSTNAME, BROKER_PORT, BROKER_USERNAME,
                              BROKER_PASSWORD, CENTRE_ID, DATASET_CONFIG,
                              DISCOVERY_METADATA_ZIP, TOPIC_PREFIX,
                              WIS2_GDC)
from msc_wis2node.util import get_mqtt_client_id, get_mqtt_tls_settings

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

    skips = ['decommissioned', 'other', 'shared', 'template']

    datasets_conf = {
        'datasets': []
    }

    if metadata_zipfile is not None or not DISCOVERY_METADATA_ZIP.startswith('http'):  # noqa
        LOGGER.debug('zipfile is a local file')
        with metadata_zipfile.open('rb') as fh:
            zipfile_content = fh.read()
    else:
        LOGGER.debug('zipfile is a URL')
        zipfile_content = urlopen(DISCOVERY_METADATA_ZIP).read()

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
                    LOGGER.info(f'Processing {path_object}')
                    mcf = read_mcf(path_object)

                    try:
                        _ = mcf['msc-metadata']['publish-to']['wmo-wis2']
                    except KeyError:
                        LOGGER.info('Metadata not in scope for publishing to WIS2')  # noqa
                        continue

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


def delete_metadata_record(identifier: str) -> bool:
    """
    Publishes a WIS2 Notification to delete a metadata record

    :param identifier: WCMP2 identifier

    :returns: `bool` of message publishing result
    """

    topic = f'{TOPIC_PREFIX}/{CENTRE_ID}/metadata'
    LOGGER.debug(f'Topic: {topic}')

    url_info = get_url_info('https://dd.weather.gc.ca')

    message = create_message(
        identifier=str(uuid.uuid4()),
        metadata_id=identifier,
        topic=topic,
        content_type='application/geo+json',
        url_info=url_info,
        operation='delete'
    )

    message['properties'].pop('integrity')
    message['properties']['data_id'] = topic
    message.pop('links')

    message['links'] = [{
        'rel': 'canonical',
        'type': 'application/geo+json',
        'href': f'{WIS2_GDC}/{identifier}'
        }, {
        'rel': 'deletion',
        'type': 'application/geo+json',
        'href': f'{WIS2_GDC}/{identifier}'
    }]

    LOGGER.debug(f'Message: {message}')

    publish.single(
        topic,
        payload=json.dumps(message),
        qos=1,
        hostname=BROKER_HOSTNAME,
        port=BROKER_PORT,
        client_id=get_mqtt_client_id(),
        tls=get_mqtt_tls_settings(),
        auth={
            'username': BROKER_USERNAME,
            'password': BROKER_PASSWORD
        }
    )

    return True


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

    click.echo('Done')


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
@click.option('--identifier', '-i', help='Metadata identifier')
def delete_metadata(ctx, identifier, verbosity):
    """Delete metadata record"""

    if identifier is None:
        raise click.ClickException('Missing metadata identifier (-i)')

    click.echo(f'Deleting metadata record {identifier}')

    delete_metadata_record(identifier)

    click.echo('Done')


dataset.add_command(setup)
dataset.add_command(delete_metadata)
