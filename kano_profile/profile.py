#!/usr/bin/env python

# profile.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
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
    ''' Read profile data from file containing profile information and return
    it as a dict. If such a file is not present, then a new dict is created
    :returns: profile data as a dict
    :rtype: dict
    '''
    data = read_json(profile_file)
    if not data:
        data = dict()
        # if the profile file doesn't exist make sure that the new one
        # is created with the right version
        data['version'] = 2
    if 'version' not in data:
        data.pop('avatar', None)
        data.pop('environment', None)
    data['username_linux'] = get_user_unsudoed()
    return data


def save_profile(data):
    ''' Write profile data to file
    :param data: JSON serialisable data about the profile
    '''
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
    ''' Update the file containing the profile data with the item
    variable -> value. This function reads from the file (and can handle the
    case where that doesn't exist) updates or creates the entry and then
    writes the file to disk. If you need to do this for multiple variables,
    consider doing it manually
    :param variable: Variable name
    :param value: value for the variable
    '''
    profile = load_profile()
    profile[variable] = value
    save_profile(profile)


def get_avatar(sync=True):
    """ Returns the information about the avatar for the specific profile. If
    the optional variable is set, there will be an attempt to sync with kano
    world to ensure that the profile is up to date.
    If no info is available about the avatar, a default set is being returned
    :param sync: (Optional) Set to True to sync before providing the values
                 for the avatar
    :type sync: Boolean
    :returns: tuple of the form (char, items) or None in case of version error
    :rtype: tuple with two items
    """
    profile = load_profile()
    if 'version' in profile and profile['version'] == 2 and \
            'avatar' in profile:
        subcat, item = profile['avatar']
    else:
        # Attempt to sync to retrieve the avatar from world
        if sync:
            block_and_sync()
            recreate_char(block=True)
            subcat, item = get_avatar(sync=False)
        else:
            # Provide a default set
            logger.info('Avatar not found in profile, returning default')
            subcat, item = get_default_avatar()
    return subcat, item


def get_default_avatar():
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


def get_avatar_circ_image_path():
    """ Returns a full path to the file that contains the asset that is being
    used as the icon stamp on the desktop. To do this, assuming the version of
    the profile structure is correct, it looks into the default avatar asset
    folder for a file with the suffix '_circ_ring.png'.
    In case of error the string that is returned is empty
    :returns: Path to circular image to be used as icon stamp
    :rtype: string
    """
    profile = load_profile()
    if 'version' not in profile or profile['version'] == 1:
        logger.error("Version field not existent or is less than 2")
        return ''
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
    """ Set the avatar in the local profile structure and optionally sync
    :param subcat: first field to be used (usually character namespace)
    :param item: Dict with the mapping from category to item
    :param sync: (Optional) sync to World
    :returns: True iff an update has happened internally, False iff the
              internal structures were up to date, None if there is a version
              issue
    :rtype: None or Boolean
    """
    profile = load_profile()
    if 'version' in profile and profile['version'] == 2:
        if type(item) != dict:
            logger.error(
                "Incompatible form of item for this version of the API"
            )
            return None
    # Check whether we are updating this value and if so, recreate the assets
    needs_update = True
    if 'avatar' in profile:
        char_ex, items_ex = profile['avatar']
        if char_ex == subcat:
            if items_ex == item:
                needs_update = False

    if needs_update:
        # Update the profile structure
        profile['avatar'] = [subcat, item]
        if sync:
            sync_profile()
        save_profile(profile)
    return needs_update


def get_environment():
    """ Return the environment
    :returns: the saved environment, or the default
    :rtype: string
    """
    profile = load_profile()
    if 'version' in profile and profile['version'] == 2 and \
            'environment' in profile:
        environment = profile['environment']
    else:
        environment = 'Dojo'
    return environment


def set_environment(environment, sync=False):
    """ Set the avatar in the local profile structure and optionally sync
    :param environment: Environment name to be used
    :param sync: (Optional) sync to World
    :returns: True iff an update has happenned internally, False iff the
              internal structures were up to date
    :rtype: Boolean
    """
    profile = load_profile()
    needs_update = True
    if 'environment' in profile:
        if profile['environment'] == environment:
            needs_update = False

    if needs_update:
        profile['environment'] = environment
        if sync:
            sync_profile()
        save_profile(profile)
    return needs_update


def sync_profile():
    """ Sync the local profile data with kano_world, without blocking
    """
    logger.info('sync_profile')
    cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
    run_bg(cmd)


def block_and_sync():
    """ Sync the local profile data with kano_world and block until finished
    """
    logger.info('block and sync profile')
    cmd = '{bin_dir}/kano-sync --sync -s --skip-kdesk'.format(bin_dir=bin_dir)
    pr = run_bg(cmd)
    pr.wait()


def recreate_char(block=True):
    """ Recreate the assets for the character from the saved values
    :param block: (Optional) Set to True to block until the operation has
                  finished
    :type block: Boolean
    """
    logger.info('recreating character from profile')
    cmd = '{bin_dir}/kano-character-cli -g'.format(bin_dir=bin_dir)
    pr = run_bg(cmd)
    if block:
        pr.wait()
