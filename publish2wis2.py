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
import os
import random
import ssl

import certifi
from paho.mqtt import publish
from pywis_pubsub.publish import create_message
from sarracenia.flowcb import FlowCB

LOGGER = logging.getLogger(__name__)


class WIS2Publisher(FlowCB):
    """WIS2 Publisher"""

    def __init__(self, options):
        """initialize"""

        self.username = os.environ['MSC_WIS2NODE_BROKER_USERNAME']
        self.password = os.environ['MSC_WIS2NODE_BROKER_PASSWORD']
        self.hostname = os.environ['MSC_WIS2NODE_BROKER_HOSTNAME']
        self.port = int(os.environ['MSC_WIS2NODE_BROKER_PORT'])

        self.client_id = f'msc-wis2node id={random.randint(0, 1000)} (https://github.com/ECCC-MSC/msc-wis2node)'  # noqa


        self.tls = {'ca_certs': certifi.where(), 'tls_version': ssl.PROTOCOL_TLSv1_2}

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
                url = f"{msg['baseUrl']}{msg['relPath']}"
                if '/IS/' not in url:
                    return
                self.publish_to_wis2(msg['filename'], url)
                new_incoming.append(msg)
            except Exception as err:
                LOGGER.error(f'Error sending to remote: {err}', exc_info=True)
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

        topic = 'origin/a/wis2/can/eccc-msc/data/core/weather/surface-based-observations/synop'  # noqa
        message = create_message(
            topic=topic,
            content_type='application/x-bufr',
            url=url,
            identifier=identifier
        )
        print(json.dumps(message, indent=4))
        LOGGER.debug('Publishing WIS2 notification message')

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

    def __repr__(self):
        return '<WIS2Publisher>'
