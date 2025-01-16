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
#
###############################################################################

import logging
import os

LOGGER = logging.getLogger(__name__)

BROKER_HOSTNAME = os.environ.get('MSC_WIS2NODE_BROKER_HOSTNAME')
BROKER_PORT = int(os.environ.get('MSC_WIS2NODE_BROKER_PORT', 8883))
BROKER_USERNAME = os.environ.get('MSC_WIS2NODE_BROKER_USERNAME')
BROKER_PASSWORD = os.environ.get('MSC_WIS2NODE_BROKER_PASSWORD')
MSC_DATAMART_AMQP = os.environ.get('MSC_WIS2NODE_MSC_DATAMART_AMQP')
DATASET_CONFIG = os.environ.get('MSC_WIS2NODE_DATASET_CONFIG')
TOPIC_PREFIX = os.environ.get('MSC_WIS2NODE_TOPIC_PREFIX', 'origin/a/wis2')
DISCOVERY_METADATA_ZIP_URL = os.environ.get('MSC_WIS2NODE_DISCOVERY_METADATA_ZIP_URL')  # noqa
CACHE = os.environ.get('MSC_WIS2NODE_CACHE')
CENTRE_ID = os.environ.get('MSC_WIS2NODE_CENTRE_ID')
WIS2_GDC = os.environ.get('MSC_WIS2NODE_WIS2_GDC')

if None in [BROKER_HOSTNAME, BROKER_PORT, BROKER_USERNAME, BROKER_PASSWORD,
            MSC_DATAMART_AMQP, DATASET_CONFIG, TOPIC_PREFIX, WIS2_GDC]:
    msg = 'Environment variables not set!'
    LOGGER.error(msg)
    raise EnvironmentError(msg)
