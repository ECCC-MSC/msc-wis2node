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

import json
import logging
import os
import random
import ssl
from typing import Union
import uuid

import certifi
from paho.mqtt import publish
from pywis_pubsub.publish import create_message
from sarracenia.flowcb import FlowCB

LOGGER = logging.getLogger(__name__)


class WIS2Publisher(FlowCB):
    """WIS2 Publisher"""

    def __init__(self, options):
        """initialize"""

        self.datasets = []
        self.tls = None
        self.dataset_config = os.environ['MSC_WIS2NODE_DATASET_CONFIG']
        self.username = os.environ['MSC_WIS2NODE_BROKER_USERNAME']
        self.password = os.environ['MSC_WIS2NODE_BROKER_PASSWORD']
        self.hostname = os.environ['MSC_WIS2NODE_BROKER_HOSTNAME']
        self.port = int(os.environ['MSC_WIS2NODE_BROKER_PORT'])
        self.topic_prefix = os.environ.get('MSC_WIS2NODE_TOPIC_PREFIX',
                                           'origin/a/wis')

        self.client_id = f'msc-wis2node id={random.randint(0, 1000)} (https://github.com/ECCC-MSC/msc-wis2node)'  # noqa

        if self.port == 8883:
            self.tls = {
                'ca_certs': certifi.where(),
                'tls_version': ssl.PROTOCOL_TLSv1_2
            }

        with open(self.dataset_config) as fh:
            self.datasets = json.load(fh)['datasets']

    def after_accept(self, worklist) -> None:
        """
        sarracenia dispatcher

        :param worklist: `sarracenia.flowcb`

        :returns: None
        """

        new_incoming = []

        for msg in worklist.incoming:
            dataset = None
            try:
                LOGGER.debug('Processing notification')
                relpath = '/' + msg['relPath'].lstrip('/')

                url = f"{msg['baseUrl']}{relpath}"
                dataset = self.identify(relpath)

                if dataset is None:
                    LOGGER.debug('Dataset not found; skipping')
                    return
                else:
                    LOGGER.debug(f'Publishing dataset notification: {url}')
                    self.publish_to_wis2(dataset, url)
                    new_incoming.append(msg)
            except Exception as err:
                LOGGER.error(f'Error publishing message: {err}', exc_info=True)
                worklist.failed.append(msg)
                continue

        worklist.incoming = new_incoming

    def identify(self, path: str) -> Union[dict, None]:
        """
        Determines whether data granule is part of a configued dataset

        :param path: `str` of topic/path

        :returns: `dict` of dataset definition or `None`
        """

        for dataset in self.datasets:
            subtopic_dirpath = self._subtopic2dirpath(dataset['subtopic'])

            if path.startswith(subtopic_dirpath):
                LOGGER.debug('Found match')
                return dataset

        LOGGER.debug('No match found')

        return None

    def publish_to_wis2(self, dataset: str, url: str) -> None:
        """
        WIS2 publisher

        :param dataset: `dict` of dataset definition
        :param url: `str` of URL of resource

        :returns: `bool` of dispatch result
        """

        topic = f"{self.topic_prefix}/{dataset['wis2-topic']}"

        message = create_message(
            identifier=str(uuid.uuid4()),
            metadata_id=dataset['metadata_id'],
            topic=topic,
            content_type='application/octet-stream',
            url=url
        )

        LOGGER.debug(json.dumps(message, indent=4))
        LOGGER.info('Publishing WIS2 notification message')

        publish.single(
            topic,
            payload=json.dumps(message),
            qos=1,
            hostname=self.hostname,
            port=self.port,
            client_id=self.client_id,
            tls=self.tls,
            auth={
                'username': self.username,
                'password': self.password
            }
        )

    def _subtopic2dirpath(self, subtopic: str) -> str:
        """
        Transforms AMQP subtopic to directory path

        :param subtopic: `str` of AMQP subtopic

        :returns: `str` of directory path
        """

        LOGGER.debug(f'AMQP subtopic: {subtopic}')

        dirpath = '/' + subtopic.replace('.', '/').rstrip('/#')

        LOGGER.debug(f'directory path: {dirpath}')

        return dirpath

    def __repr__(self):

        return '<WIS2Publisher>'
