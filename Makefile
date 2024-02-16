# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2024 Tom Kralidis
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

# Ubuntu
SR3_CONFIG=${HOME}/.config/sr3

# Mac OSX
#SR3_CONFIG=${HOME}/Library/Application\ Support/sr3

check:
	@echo "SR3 configuration directory: ${SR3_CONFIG}"

install: setup
	cp msc_wis2node/publisher.py $(SR3_CONFIG)/plugins
	cp deploy/default/sarracenia/dd.weather.gc.ca-all.conf $(SR3_CONFIG)/subscribe

setup:
	mkdir -p $(SR3_CONFIG)/plugins
	mkdir -p $(SR3_CONFIG)/subscribe

clean:
	rm -fr $(SR3_CONFIG)/plugins/publisher.py
	rm -fr $(SR3_CONFIG)/subscribe/dd.weather.gc.ca-all.conf

.PHONY: check install setup clean
