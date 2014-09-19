#!/usr/bin/env python

# profile.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

"""
Profile module

This module provides functions to store and retreive profile related information
for the user.
These informations are stored in `~/.kanoprofile/profile/profile.json`

Application specific informations are stored in the app module.
"""

import os

from kano.logging import logger
from kano.utils import read_json, write_json, get_date_now, ensure_dir, chown_path, \
    get_user_unsudoed, run_bg, is_running
from .paths import profile_file, profile_dir, kanoprofile_dir, bin_dir


def load_profile():
    """Returns a dict object of the current profile state"""

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
    """Saves a dict object to the current profile state, overwriting it"""

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

    if os.path.exists('/usr/bin/kdesk') and not is_running('kano-sync'):
        logger.info('refreshing kdesk from save_profile')
        run_bg('kdesk -a profile')


def save_profile_variable(variable, value):
    """Sets the 'variable' key of profile to 'value'"""

    profile = load_profile()
    profile[variable] = value
    save_profile(profile)


def set_unlocked(boolean):
    """Unlocks the profile"""

    logger.debug('set_unlocked {}'.format(boolean))

    profile = load_profile()
    profile['unlocked'] = boolean
    save_profile(profile)


def is_unlocked():
    """Returns the unlocked state of the profile"""

    profile = load_profile()
    if 'unlocked' in profile:
        return load_profile()['unlocked']
    else:
        return False


def get_avatar():
    """Returns the actual avatar of the user, in "subcat, item" tuple"""

    profile = load_profile()
    if 'avatar' in profile:
        subcat, item = profile['avatar']
    else:
        subcat = 'judoka'
        item = 'judoka_1'
    return subcat, item


def set_avatar(subcat, item, sync=False):
    """Sets the avatar for the user, specified via subcat, item"""

    profile = load_profile()
    profile['avatar'] = [subcat, item]
    save_profile(profile)
    if sync:
        sync_profile()


def get_environment():
    """Returns the actual environment of the user"""

    profile = load_profile()
    if 'environment' in profile:
        environment = profile['environment']
    else:
        environment = 'dojo'
    return environment


def set_environment(environment, sync=False):
    """Sets the environment for the user"""

    profile = load_profile()
    profile['environment'] = environment
    save_profile(profile)
    if sync:
        sync_profile()


def sync_profile():
    """A helper command for running kano-sync --sync -s"""

    logger.info('sync_profile')
    cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
    run_bg(cmd)
