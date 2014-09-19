#!/usr/bin/env python

# apps.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

"""
Apps module

This module provides functions to store and retrieve app related
information for the user.the

These informations are stored in '~/.kanoprofile/apps/{appname}/state.json'
"""

import os

from kano.utils import read_json, write_json, get_date_now, ensure_dir, chown_path, \
    run_print_output_error, is_running, run_bg
from kano.logging import logger
from .paths import apps_dir, xp_file, kanoprofile_dir, app_profiles_file
from .profile import is_unlocked


def get_app_dir(app_name):
    """Gets the full path of an app's directory in the kanoprofile/apps folder"""

    app_dir = os.path.join(apps_dir, app_name)
    return app_dir


def get_app_data_dir(app_name):
    """Gets the full path of an app's data directory in the kanoprofile/apps folder"""

    data_str = 'data'
    app_data_dir = os.path.join(get_app_dir(app_name), data_str)
    return app_data_dir


def get_app_state_file(app_name):
    """Gets the full path of an app's state.json file in the kanoprofile/apps folder"""

    app_state_str = 'state.json'
    app_state_file = os.path.join(get_app_dir(app_name), app_state_str)
    return app_state_file


def load_app_state(app_name):
    """Returns a dict object of the current app's state"""

    app_state_file = get_app_state_file(app_name)
    app_state = read_json(app_state_file)
    if not app_state:
        app_state = dict()
    return app_state


def load_app_state_variable(app_name, variable):
    """Returns value of the 'variable' key from the current profile state"""

    data = load_app_state(app_name)
    if is_unlocked():
        data['level'] = 999
    if variable in data:
        return data[variable]


def save_app_state(app_name, data):
    """Updates and overwrites the app's state with the given data dict"""

    logger.debug('save_app_state {}'.format(app_name))

    if is_unlocked():
        try:
            data['level'] = load_app_state(app_name)['level']
        except Exception:
            pass

    app_state_file = get_app_state_file(app_name)
    data['save_date'] = get_date_now()
    ensure_dir(get_app_dir(app_name))
    write_json(app_state_file, data)
    if 'SUDO_USER' in os.environ:
        chown_path(kanoprofile_dir)
        chown_path(apps_dir)
        chown_path(get_app_dir(app_name))
        chown_path(app_state_file)

    # Ask kdesk to refresh the Login/Register icon with new Kano Level
    if os.path.exists('/usr/bin/kdesk') and not is_running('kano-sync'):
        logger.info('refreshing kdesk from save_app_state')
        run_bg('kdesk -a profile')


def save_app_state_variable(app_name, variable, value):
    """Updates and overwrites app_state[variable] with value"""

    logger.debug('save_app_state_variable {} {} {}'.format(app_name, variable, value))

    if is_unlocked() and variable == 'level':
        return
    data = load_app_state(app_name)
    data[variable] = value

    save_app_state(app_name, data)


def increment_app_state_variable(app_name, variable, value):
    """Increments the numeric value app_state[variable] with value"""

    logger.debug('increment_app_state_variable {} {} {}'.format(app_name, variable, value))

    if is_unlocked() and variable == 'level':
        return
    data = load_app_state(app_name)
    if variable not in data:
        data[variable] = 0
    data[variable] += value

    save_app_state(app_name, data)


def get_app_list():
    """Returns a list of all apps which have a directory in .kanoprofile/apps"""

    if not os.path.exists(apps_dir):
        return []
    else:
        return [p for p in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, p))]


def get_gamestate_variables(app_name):
    """Returns all keys specified in the xp.json file"""

    allrules = read_json(xp_file)
    if not allrules:
        return list()

    groups = allrules[app_name]

    for group, rules in groups.iteritems():
        if group == 'multipliers':
            return [str(key) for key in rules.keys()]


def launch_project(app, filename, data_dir):
    """Launches an application to load a file (for example a save game)
    The command line is specified in the app_profiles.json file"""

    logger.info('launch_project: {} {} {}'.format(app, filename, data_dir))

    app_profiles = read_json(app_profiles_file)

    fullpath = os.path.join(data_dir, filename)
    cmd = app_profiles[app]['cmd'].format(fullpath=fullpath, filename=filename)
    run_print_output_error(cmd)
