# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2023 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import json
import logging

from pywis_pubsub.mqtt import MQTTPubSubClient
from pywis_pubsub.publish import create_message
from sarracenia.flowcb import FlowCB

LOGGER = logging.getLogger(__name__)


class WIS2Publisher(FlowCB):
    """WIS2 Publisher"""

    def __init__(self, options):
        """initialize"""

        self.options = options

    def after_accept(self, worklist) -> None:
        """
        sarracenia dispatcher

        :param worklist: `sarracenia.flowcb`

        :returns: None
        """

        new_incoming = []

        for msg in worklist.incoming:
            try:
                LOGGER.debug('Processing notification')
                url = f'{msg.baseUrl}{msg.relPath}'
                self.publish_to_wis2(msg.filename, url)
                new_incoming.append(msg)
            except Exception as err:
                LOGGER.error(f'Error sending to remote: {err}')
                worklist.failed.append(msg)
                continue

        worklist.incoming = new_incoming

    def publish_to_wis2(self, identifier: str, url: str) -> None:
        """
        WIS2 publisher

        :param identifier: `str` of identifier
        :param url: `str` of URL of resource

        :returns: `bool` of dispatch result
        """

        topic = 'origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations',
        message = create_message(
            topic=topic,
            content_type='application/x-bufr',
            url=url,
            identifier=identifier
        )
        LOGGER.debug('Publishing WIS2 notification message')
        m = MQTTPubSubClient('mqtt://mscwis2user:mscwis2user@a2ea81cfe2b44453992b427ed2abe9cd.s2.eu.hivemq.cloud:8883')
        m.pub(topic, json.dumps(message))

    def __repr__(self):
        return '<WIS2Publisher>'
