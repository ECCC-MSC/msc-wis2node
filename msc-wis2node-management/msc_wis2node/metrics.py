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

import logging

import click
import redis

from msc_wis2node import cli_options
from msc_wis2node.env import CACHE

LOGGER = logging.getLogger(__name__)


def get_metrics() -> dict:
    """
    Export and purge data distribution metrics

    :returns: `None`
    """

    metrics = {}

    r = redis.Redis().from_url(CACHE)

    for key in r.scan_iter('metrics_20*'):
        LOGGER.debug(f'Key: {key}')
        _, _, dataset, metric = str(key).split('_')

        if dataset not in metrics:
            metrics[dataset] = {
                metric: r.get(key)
            }
        else:
            metrics[dataset][metric] = r.get(key)

        LOGGER.debug(f'Deleting key: {key}')
        r.delete(key)

    return metrics


@click.group()
def metrics():
    """Metrics management"""

    pass


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
def collect_metrics(ctx, verbosity):
    """Setup dataset definitions"""

    click.echo('Collecting metrics')

    click.echo(get_metrics())

    click.echo('Done')


metrics.add_command(collect_metrics)
