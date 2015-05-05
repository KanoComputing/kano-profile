#!/usr/bin/env python

# config.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import yaml

CONF_FILE = '/etc/kano-world.conf'


def load_conf():
    conf = None
    if os.path.exists(CONF_FILE):
        with open(CONF_FILE, 'r') as f:
            conf = yaml.load(f)

    if conf is None:
        conf = {}

    if 'api_url' not in conf:
        conf['api_url'] = 'https://api.kano.me'

    if 'world_url' not in conf:
        conf['world_url'] = 'http://world.kano.me'

    return conf


CONF = load_conf()

API_URL = CONF['api_url']
WORLD_URL = CONF['world_url']


def get_world_url(path):
    return "{}/{}".format(WORLD_URL, path)


def get_api_url(path):
    return "{}/{}".format(API_URL, path)
