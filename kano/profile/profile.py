#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from ..utils import read_json, write_json, get_cpu_id, get_mac_address, get_date_now
from .paths import profile_file, linux_user


def load_profile():
    data = read_json(profile_file)
    if not data:
        data = dict()

    if 'username_linux' not in data:
        data['username_linux'] = linux_user

    if 'cpu_id' not in data and get_cpu_id():
        data['device_id'] = get_cpu_id()

    if 'mac_addr' not in data and get_mac_address():
        data['mac_addr'] = get_mac_address()

    return data


def save_profile(data):
    data['last_save_date'] = get_date_now()
    write_json(profile_file, data)


def set_unlocked(boolean):
    profile = load_profile()
    profile['unlocked'] = boolean
    save_profile(profile)


def is_unlocked():
    profile = load_profile()
    if 'unlocked' in profile:
        return load_profile()['unlocked']
    else:
        return False
