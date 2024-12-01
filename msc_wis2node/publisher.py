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

from datetime import date, datetime, timezone
from fnmatch import fnmatch
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
import yaml

from msc_wis2node.env import (BROKER_HOSTNAME, BROKER_PORT, BROKER_USERNAME,
                              BROKER_PASSWORD, CENTRE_ID, DATASET_CONFIG,
                              TOPIC_PREFIX)

LOGGER = logging.getLogger(__name__)


class WIS2FlowCB(FlowCB):
    def __init__(self, options):
        super().__init__(options,LOGGER)
        self.o.add_option('selfPublish', 'flag', True)
        self.wis2_nonPublisher = WIS2Publisher()
        
    def after_accept(self, worklist) -> None:
        """
        sarracenia dispatcher

        :param worklist: `sarracenia.flowcb`

        :returns: None
        """

        new_incoming = []

        for msg in worklist.incoming:
            try:
                LOGGER.debug('Processing message')

                if self.o.selfPublish:
                    wis2_publisher = WIS2Publisher()
                    if wis2_publisher.publish(msg['baseUrl'], msg['relPath']):
                        new_incoming.append(msg)
                    else:
                        worklist.rejected.append(msg)
                else:
                    dataset = self.wis2_nonPublisher.identify(msg['relPath'])
                    if dataset:

                    
                        # 2024-03-15 19:40:44,350 [CRITICAL] 2782038 publisher publish Dataset: {'metadata-id': 'c944aca6-0d59-418c-9d91-23247c8ada17', 'regexes': ['.*ISA[A|B]0[1-6].*'], 'title': 'Hourly surface based observations', 'subtopic': 'bulletins.alphanumeric.*.IS.CWAO.#', 'wis2-topic': 'data/core/weather/surface-based-observations/synop', 'media-type': 'application/x-bufr', 'cache': True}
                        msg["topic"] = self.o.post_exchange[0] + "/" + "/".join(self.o.post_topicPrefix) + "/" + dataset["wis2-topic"]

                        msg["data_id"] = dataset["wis2-topic"] + "/" + msg["relPath"].split("/")[-1]
                        # wis2/ca-eccc-msc - missing from start
                        msg["contentType"] = dataset["media-type"]

                        new_incoming.append(msg)

                    else:
                        worklist.rejected.append(msg)

            except Exception as err:
                LOGGER.error(f'Error publishing message: {err}', exc_info=True)
                worklist.failed.append(msg)

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
            self.datasets = yaml.load(fh, Loader=yaml.SafeLoader)['datasets']

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
            LOGGER.debug(f'{dataset = }')
            match = False
            subtopic_dirpath = self._subtopic2dirpath(dataset['subtopic'])

            LOGGER.debug(f'Testing subtopic match: {subtopic_dirpath}')
            if fnmatch(path, subtopic_dirpath):
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
            else:
                LOGGER.debug('NO MATCH')
                LOGGER.debug(path)
                LOGGER.debug(subtopic_dirpath)

        LOGGER.debug('No match found')

        return None

    def publish_to_wis2(self, dataset: dict, url: str) -> None:
        """
        WIS2 publisher

        :param dataset: `dict` of dataset definition
        :param url: `str` of URL of resource

        :returns: `bool` of dispatch result
        """

        topic = f"{TOPIC_PREFIX}/{CENTRE_ID}/{dataset['wis2-topic']}"
        LOGGER.info(f'URL: {url}')

        datetime_ = self._topic_regex2datetime(
            url, dataset.get('msc-filename-datetime-regex'))

        metadata_id = f"urn:wmo:md:{CENTRE_ID}:{dataset['metadata-id']}"

        message = create_message(
            identifier=str(uuid.uuid4()),
            metadata_id=metadata_id,
            datetime_=datetime_,
            topic=topic,
            content_type=dataset['media-type'],
            url=url
        )

        cache = dataset.get('cache', True)
        if not cache:
            LOGGER.info(f'Setting properties.cache={cache}')
            message['properties']['cache'] = False

        LOGGER.debug('Removing system and version from data_id')
        data_id = message['properties']['data_id']
        tokens = data_id.split('/')
        message['properties']['data_id'] = '/'.join(tokens[2:])

        LOGGER.info(json.dumps(message, indent=4))
        msg = (f'Publishing WIS2 notification message to '
               f'host={BROKER_HOSTNAME}, port={BROKER_PORT}, topic={topic}')
        LOGGER.info(msg)

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
        dirpath = f'*{dirpath}*'

        LOGGER.debug(f'directory path: {dirpath}')

        return dirpath

    def _topic_regex2datetime(self, topic: str,
                              pattern: Union[str, None]) -> Union[str, None]:
        """
        Generate RFC3339 string

        :param topic: topic
        :param pattern: regular expression of date pattern

        :returns: `str` of resulting RFC3339 datetime, or `None` if not found
        """

        if pattern is None:
            return None

        match = re.search(topic, pattern)

        if match is None:
            LOGGER.debug(f'No match ({pattern} not in {topic})')
            return None

        groups = [int(m) for m in match.groups()]
        LOGGER.debug(f'datetime regex groups found: {groups}')

        if len(groups) < 3:
            LOGGER.debug('Casting date')
            obj = date(*groups)
            value = obj.isoformat()
        else:
            LOGGER.debug('Casting datetime')
            dt = datetime(*groups, tzinfo=timezone.utc)
            value = f'{dt.isoformat()}Z'

        return value

    def __repr__(self):
        return '<WIS2Publisher>'
