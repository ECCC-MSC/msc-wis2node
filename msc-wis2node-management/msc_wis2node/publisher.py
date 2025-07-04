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

from copy import deepcopy
from datetime import date, datetime, timezone
from fnmatch import fnmatch
import json
import logging
import re
from typing import Union
import uuid

from paho.mqtt import publish
from pywis_pubsub.publish import create_message
import redis
from sarracenia.flowcb import FlowCB
import yaml

from msc_wis2node.env import (BROKER_HOSTNAME, BROKER_PORT, BROKER_USERNAME,
                              BROKER_PASSWORD, CACHE, CACHE_EXPIRY_SECONDS,
                              CENTRE_ID, DATASET_CONFIG, TOPIC_PREFIX)
from msc_wis2node.util import get_mqtt_client_id, get_mqtt_tls_settings

LOGGER = logging.getLogger(__name__)


class WIS2FlowCB(FlowCB):
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

        self.cache = None
        self.datasets = []
        self.tls = None

        self.client_id = get_mqtt_client_id()

        if CACHE is not None:
            self.cache = redis.Redis().from_url(CACHE)

        if BROKER_PORT == 8883:
            self.tls = get_mqtt_tls_settings()

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

        relative_path2 = relative_path.lstrip('/')
        base_url2 = base_url.rstrip('/')
        url = f'{base_url2}/{relative_path2}'

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
            LOGGER.debug(f'Dataset: {dataset}')
            match = False
            subtopic_dirpath = self._subtopic2dirpath(dataset['subtopic'])

            LOGGER.debug(f'Testing subtopic match: {subtopic_dirpath}')
            if fnmatch(path, subtopic_dirpath):
                LOGGER.debug('Found matching subtopic')
                match = True

                for regex in dataset.get('regexes', []):
                    match = False
                    LOGGER.debug(f'Testing regex match: {regex}')
                    if re.search(regex, path) is not None:
                        LOGGER.debug('Found matching regex')
                        match = True
                        break

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

        if self.cache is not None:
            LOGGER.info(f"Checking for duplicate: {message['properties']['data_id']}")  # noqa
            if self.cache.get(message['properties']['data_id']) is not None:
                update_link = deepcopy(message['links'][0])
                update_link['rel'] = 'update'
                message['links'].append(update_link)

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

        if self.cache is not None:
            LOGGER.info(f"Setting cache key for {message['properties']['data_id']}")  # noqa
            self.cache.set(message['properties']['data_id'], 'published',
                           ex=CACHE_EXPIRY_SECONDS)

        LOGGER.info('Updating dataset distribution metrics')
        self._update_dataset_distribution_metrics(
            metadata_id, message['links'][0]['length'])

    def _update_dataset_distribution_metrics(self, metadata_id, filesize) -> None:  # noqa
        """
        Set/update dataset distrubution metrics

        :param metadata_id: metadata identifier
        :param length: metadata identifier

        :returns: `None`
        """

        today = datetime.today().strftime('%Y-%m-%d')

        dataset_files_cache_key = f'metrics_{today}_{metadata_id}_files'
        dataset_bytes_cache_key = f'metrics_{today}_{metadata_id}_bytes'

        total_files_cache_key = f'metrics_total_{today}_files'
        total_bytes_cache_key = f'metrics_total_{today}_bytes'

        LOGGER.debug('Incrementing dataset number of files published')
        self.cache.incr(dataset_files_cache_key)

        LOGGER.debug('Incrementing all total number of files published')
        self.cache.incr(total_files_cache_key)

        LOGGER.debug('Updating dataset total bytes')
        dataset_bytes = self.cache.get(dataset_bytes_cache_key)

        if dataset_bytes is None:
            self.cache.set(dataset_bytes_cache_key, filesize)
        else:
            self.cache.set(
                dataset_bytes_cache_key, int(dataset_bytes) + filesize
            )

        LOGGER.debug('Updating all total bytes')
        total_bytes = self.cache.get(total_bytes_cache_key)

        if total_bytes is None:
            self.cache.set(total_bytes_cache_key, filesize)
        else:
            self.cache.set(
                total_bytes_cache_key, int(total_bytes) + filesize
            )

        return None

    def _subtopic2dirpath(self, subtopic: str) -> str:
        """
        Transforms AMQP subtopic to directory path

        :param subtopic: `str` of AMQP subtopic

        :returns: `str` of directory path
        """

        LOGGER.debug(f'AMQP subtopic: {subtopic}')

        dirpath = '/' + subtopic.replace('*.', '/').replace('.', '/').rstrip('/#')  # noqa
        dirpath = dirpath.replace('//', '/')
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
