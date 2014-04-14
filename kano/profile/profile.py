#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from ..utils import read_json, write_json, get_cpu_id, get_mac_address, get_date_now, ensure_dir
from .paths import profile_file, profile_dir, linux_user


def load_profile():
    data = read_json(profile_file)
    if not data:
        data = dict()

    data['username_linux'] = linux_user

    if get_cpu_id():
        data['cpu_id'] = get_cpu_id()

    if get_mac_address():
        data['mac_addr'] = get_mac_address()

    return data


def save_profile(data):
    data.pop('cpu_id', None)
    data.pop('mac_addr', None)
    data['save_date'] = get_date_now()
    ensure_dir(profile_dir)
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
