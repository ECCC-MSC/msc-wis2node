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

import logging
import os
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
                filepath = f"{os.sep}{['relPath']}"
                LOGGER.debug(f'Local filepath: {filepath}')

                identifier = os.path.basename(filepath)

                self.publish_to_wis2(msg=msg, filepath=filepath)
                new_incoming.append(msg)
            except Exception as err:
                LOGGER.error(f'Error sending to remote: {err}')
                worklist.failed.append(msg)
                continue

        worklist.incoming = new_incoming

    def publish_to_wis2(self, msg, filepath: str) -> None:
        """
        WIS2 publisher

        :param filepath: `str` of local filepath to upload

        :returns: `bool` of dispatch result
        """

        remote_filepath = filepath.lstrip("/")

    def __repr__(self):
        return '<WIS2Publisher>'
