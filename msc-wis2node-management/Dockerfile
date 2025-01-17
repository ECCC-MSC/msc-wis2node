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

FROM ubuntu:jammy

LABEL maintainer="tomkralidis@gmail.com"

ARG SR3_CONFIG /home/msc-wis2node/.config/sr3

ENV TZ="Etc/UTC" \
    DEBIAN_FRONTEND="noninteractive" \
    DEBIAN_PACKAGES="bash curl git python3-pip python3-setuptools sudo vim"

# copy the app 
COPY ./ /app

RUN apt-get update -y && \
    # install dependencies
    apt-get install -y ${DEBIAN_PACKAGES} && \
    pip3 install --no-cache-dir -r /app/requirements.txt && \
    # install msc-wis2node
    cd /app && \
    pip3 install -e . && \
    chmod +x /app/docker/entrypoint.sh && \
    # cleanup
    apt autoremove -y && \
    apt-get -q clean && \
    rm -rf /var/lib/apt/lists/* && \
    # add msc-wis2node user
    useradd -ms /bin/bash msc-wis2node && \
    adduser msc-wis2node sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    # install sr3 components
    mkdir -p /home/msc-wis2node/.config/sr3/plugins && \
    mkdir -p /home/msc-wis2node/.config/sr3/subscribe && \
    cp msc_wis2node/publisher.py /home/msc-wis2node/.config/sr3/plugins/publisher.py && \
    cp deploy/default/sarracenia/dd.weather.gc.ca-all.conf /home/msc-wis2node/.config/sr3/subscribe/dd.weather.gc.ca-all.conf

USER msc-wis2node
WORKDIR /home/msc-wis2node

ENTRYPOINT [ "/app/docker/entrypoint.sh" ]
