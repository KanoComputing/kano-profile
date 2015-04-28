#!/usr/bin/env python

# profile.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.logging import logger
from kano.utils import (read_json, write_json, get_date_now, ensure_dir,
                        chown_path, get_user_unsudoed, run_bg, is_running,
                        list_dir)
from .paths import profile_file, profile_dir, kanoprofile_dir, bin_dir
from kano_avatar.paths import AVATAR_DEFAULT_LOC


def load_profile():
    data = read_json(profile_file)
    if not data:
        data = dict()
        # if the profile file doesn't exist make sure that the new one
        # is created with the right version
        data['version'] = 2
    data['username_linux'] = get_user_unsudoed()
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

    if os.path.exists('/usr/bin/kdesk') and not is_running('kano-sync'):
        logger.info('refreshing kdesk from save_profile')
        run_bg('kdesk -a profile')


def save_profile_variable(variable, value):
    profile = load_profile()
    profile[variable] = value
    save_profile(profile)


def get_avatar(sync=True):
    profile = load_profile()
    if 'version' not in profile or profile['version'] == 1:
        if 'avatar' in profile:
            subcat, item = profile['avatar']
        else:
            subcat = 'judoka'
            item = 'judoka_1'
        return subcat, item
    elif profile['version'] == 2:
        if 'avatar' in profile:
            subcat, item = profile['avatar']
        else:
            # Attempt to sync to retrieve the avatar from world
            if sync:
                block_and_sync()
                subcat, item = get_avatar(sync=False)
            else:
                # Provide a default set
                logger.info('Avatar not found in profile, returning default')
                subcat = 'Judoka_Base'
                item = {
                    'Belts': 'Belt_Orange',
                    'Suits': 'Suit_White',
                    'Faces': 'Face_Happy',
                    'Hair': 'Hair_Black',
                    'Stickers': 'Sticker_Code',
                    'Skins': 'Skin_Orange',
                }

        return subcat, item
    else:
        logger.error(
            'Unknown profile version: {}'.format(profile['version'])
        )
        return None


def get_avatar_circ_image_path():
    profile = load_profile()
    if 'version' not in profile or profile['version'] == 1:
        avatar_cat, avatar_item = get_avatar()
        avatar_image_path = os.path.join(
            '/usr/share/kano-profile/media/images/avatars/54x54/',
            avatar_cat,
            '{}_white_circular.png'.format(avatar_item)
        )
        return avatar_image_path
    elif profile['version'] == 2:
        direc = AVATAR_DEFAULT_LOC
        dirs = list_dir(direc)
        circ = [fl for fl in dirs if fl.endswith('_circ_ring.png')]
        if len(circ) == 0:
            logger.error("Couldn't find a file with the appropriate suffix")
            return ''
        elif len(circ) == 1:
            return os.path.join(direc, circ[0])
        elif len(circ) > 1:
            # Return the first one but inform about the existance of multiple
            logger.warn(
                "There are more than one files with appropriate suffix"
            )
            return os.path.join(direc, circ[0])
    else:
        logger.error(
            'Unknown profile version: {}'.format(profile['version'])
        )
        return ''


def set_avatar(subcat, item, sync=False):
    profile = load_profile()
    if 'version' in profile and profile['version'] == 2:
        if type(item) != dict:
            logger.error(
                "Incompatible form of item for this version of the API"
            )
            return None
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

def block_and_sync():
    logger.info('block and sync profile')
    cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
    pr = run_bg(cmd)
    pr.wait()
