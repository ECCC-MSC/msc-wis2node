###############################################################################
#
# Copyright (C) 2025 Tom Kralidis
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

import json
import logging

import click
import redis
import yaml

from msc_wis2node import cli_options
from msc_wis2node.env import CACHE, DATASET_CONFIG

LOGGER = logging.getLogger(__name__)

METRICS_KEY_PATTERN = 'metrics_20*'


def get_metrics() -> dict:
    """
    Export and purge data distribution metrics

    :returns: `None`
    """

    metrics = {}

    r = redis.Redis().from_url(CACHE)

    for key in r.scan_iter(METRICS_KEY_PATTERN):
        LOGGER.debug(f'Key: {key}')

        _, _, dataset, metric = key.decode().split('_')

        dataset = dataset.split(':')[-1]

        if metric.endswith('bytes'):
            value = prettybytes(int(r.get(key)))
        else:
            value = int(r.get(key))

        if dataset not in metrics:
            metrics[dataset] = {
                metric: value
            }
        else:
            metrics[dataset][metric] = value

    with open(DATASET_CONFIG) as fh:
        dataset_config = yaml.safe_load(fh)

        for ds in dataset_config['datasets']:
            if ds['metadata-id'] in metrics:
                metrics[ds['metadata-id']]['title'] = ds['title']
                metrics[ds['metadata-id']]['wis2-topic'] = ds['wis2-topic']

    return metrics


def delete_metrics() -> None:
    """
    Delete metrics against a given pattern

    :returns: `None`
    """

    r = redis.Redis().from_url(CACHE)
    for key in r.scan_iter(METRICS_KEY_PATTERN):
        LOGGER.debug(f'Deleting key: {key}')
        r.delete(key)


def prettybytes(numbytes: int) -> str:
    """
    Convert bytes to human readable value

    modified from: https://gist.github.com/shawnbutts/3906915

    :param numbytes: number of bytes

    :returns: `str` of human readable bytesize

    """

    a = {'Kb': 1, 'Mb': 2, 'Gb': 3, 'Tb': 4, 'Pb': 5, 'Eb': 6}

    r = float(numbytes)

    length = len(str(numbytes))

    if 14 >= length > 12:
        to = 'Tb'
    if 12 >= length > 9:
        to = 'Gb'
    elif 9 >= length > 7:
        to = 'Mb'
    elif 7 >= length:
        to = 'Kb'

    for i in range(a[to]):
        r = r / 1024

    value = round(r, 2)

    return f'{value} {to}'


@click.group()
def metrics():
    """Metrics management"""

    pass


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
def get(ctx, verbosity):
    """Get data distribution metrics"""

    click.echo('Collecting metrics')

    click.echo(json.dumps(get_metrics(), indent=4))

    click.echo('Done')


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
def delete(ctx, verbosity):
    """Delete data distribution metrics"""

    click.echo('Collecting metrics')

    delete_metrics()

    click.echo('Done')


metrics.add_command(get)
metrics.add_command(delete)
