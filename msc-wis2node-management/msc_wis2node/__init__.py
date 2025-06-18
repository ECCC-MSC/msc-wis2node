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

__version__ = '0.1.0'

import click

from msc_wis2node.dataset import dataset
from msc_wis2node.metrics import metrics


@click.group()
@click.version_option(version=__version__)
def cli():
    """MSC WIS2 Node management utility"""

    pass


cli.add_command(dataset)
cli.add_command(metrics)
