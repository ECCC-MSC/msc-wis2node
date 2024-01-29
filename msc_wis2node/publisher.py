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
import random
import re
import ssl
from typing import Union
import uuid

import certifi
from paho.mqtt import publish
from pywis_pubsub.publish import create_message
from sarracenia.flowcb import FlowCB

from msc_wis2node.env import (BROKER_HOSTNAME, BROKER_PORT, BROKER_USERNAME,
                              BROKER_PASSWORD, DATASET_CONFIG, TOPIC_PREFIX)

LOGGER = logging.getLogger(__name__)


class WIS2FlowCB(FlowCB):
    def after_accept(self, worklist) -> None:
        """
        sarracenia dispatcher

        :param worklist: `sarracenia.flowcb`

        :returns: None
        """

        LOGGER.debug('JJJ')
        new_incoming = []

        for msg in worklist.incoming:
            try:
                LOGGER.debug('Processing message')

                wis2_publisher = WIS2Publisher()

                if wis2_publisher.publish(msg['baseUrl'], msg['relPath']):
                    new_incoming.append(msg)
                else:
                    return
            except Exception as err:
                LOGGER.error(f'Error publishing message: {err}', exc_info=True)
                worklist.failed.append(msg)
                continue

        worklist.incoming = new_incoming


class WIS2Publisher:
    """WIS2 Publisher"""

    def __init__(self):
        """initialize"""

        self.datasets = []
        self.tls = None

        self.client_id = f'msc-wis2node id={random.randint(0, 1000)} (https://github.com/ECCC-MSC/msc-wis2node)'  # noqa

        if BROKER_PORT == 8883:
            self.tls = {
                'ca_certs': certifi.where(),
                'tls_version': ssl.PROTOCOL_TLSv1_2
            }

        with open(DATASET_CONFIG) as fh:
            self.datasets = json.load(fh)['datasets']

    def publish(self, base_url: str, relative_path: str) -> bool:
        """
        Publish notification message

        :param base_url: base URL of HTTP endpoint of filepath
        :param relative_path: relative filepath

        :returns: `bool` of publishing result
        """

        dataset = self.identify(relative_path)

        if dataset is None:
            LOGGER.debug('Dataset not found; skipping')
            return False

        relative_path2 = '/' + relative_path.lstrip('/')
        url = f'{base_url}{relative_path2}'

        LOGGER.debug(f'Publishing dataset notification: {url}')
        self.publish_to_wis2(dataset, url)

        return True

    def identify(self, path: str) -> Union[dict, None]:
        """
        Determines whether data granule is part of a configured
        dataset definition

        :param path: `str` of topic/path

        :returns: `dict` of dataset definition or `None`
        """

        for dataset in self.datasets:
            match = False
            subtopic_dirpath = self._subtopic2dirpath(dataset['subtopic'])

            LOGGER.debug(f'Testing subtopic match: {subtopic_dirpath}')
            if path.startswith(subtopic_dirpath):
                LOGGER.debug('Found matching subtopic')
                match = True

                LOGGER.debug('Matching any regexes')
                for regex in dataset.get('regexes', []):
                    pass
                    LOGGER.debug(f'Testing regex match: {regex}')
                    if re.search(regex, path) is not None:
                        LOGGER.debug('Found matching regex')
                    else:
                        match = False

                if match:
                    LOGGER.debug('Found matching dataset definition')
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

        topic = f"{TOPIC_PREFIX}/{dataset['wis2-topic']}"
        LOGGER.info(f'TOPIC: {topic}')

        message = create_message(
            identifier=str(uuid.uuid4()),
            # metadata_id=dataset['metadata-id'],
            topic=topic,
            content_type=dataset['media-type'],
            url=url
        )

        LOGGER.debug('Removing system and version from data_id')
        data_id = message['properties']['data_id']
        tokens = data_id.split('/')
        message['properties']['data_id'] = '/'.join(tokens[2:])

        LOGGER.debug(json.dumps(message, indent=4))
        LOGGER.info('Publishing WIS2 notification message')

        publish.single(
            topic,
            payload=json.dumps(message),
            qos=1,
            hostname=BROKER_HOSTNAME,
            port=BROKER_PORT,
            client_id=self.client_id,
            tls=self.tls,
            auth={
                'username': BROKER_USERNAME,
                'password': BROKER_PASSWORD
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
