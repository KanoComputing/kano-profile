#!/usr/bin/env python

# profile.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.logging import logger
from kano.utils import read_json, write_json, get_date_now, ensure_dir, chown_path, \
    get_user_unsudoed, run_bg
from .paths import profile_file, profile_dir, kanoprofile_dir, bin_dir


def load_profile():
    data = read_json(profile_file)
    if not data:
        data = dict()
    data['username_linux'] = get_user_unsudoed()
    # if get_cpu_id():
        # data['cpu_id'] = get_cpu_id()
    # if get_mac_address():
        # data['mac_addr'] = get_mac_address()
    return data


def save_profile(data):
    logger.debug('save_profile')

    data.pop('cpu_id', None)
    data.pop('mac_addr', None)
    data['save_date'] = get_date_now()
    ensure_dir(profile_dir)
    write_json(profile_file, data)

    if 'SUDO_USER' in os.environ:
        chown_path(kanoprofile_dir)
        chown_path(profile_dir)
        chown_path(profile_file)

    if os.path.exists('/usr/bin/kdesk'):
        run_bg('kdesk -a profile')


def save_profile_variable(variable, value):
    profile = load_profile()
    profile[variable] = value
    save_profile(profile)


def set_unlocked(boolean):
    logger.debug('set_unlocked {}'.format(boolean))

    profile = load_profile()
    profile['unlocked'] = boolean
    save_profile(profile)


def is_unlocked():
    profile = load_profile()
    if 'unlocked' in profile:
        return load_profile()['unlocked']
    else:
        return False


def get_avatar():
    profile = load_profile()
    if 'avatar' in profile:
        subcat, item = profile['avatar']
    else:
        subcat = 'judoka'
        item = 'judoka_1'
    return subcat, item


def set_avatar(subcat, item, sync=False):
    profile = load_profile()
    profile['avatar'] = [subcat, item]
    save_profile(profile)
    if sync:
        sync_profile()


def get_environment():
    profile = load_profile()
    if 'environment' in profile:
        environment = profile['environment']
    else:
        environment = 'dojo'
    return environment


def set_environment(environment, sync=False):
    profile = load_profile()
    profile['environment'] = environment
    save_profile(profile)
    if sync:
        sync_profile()


def sync_profile():
    logger.info('sync_profile')
    cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
    run_bg(cmd)
