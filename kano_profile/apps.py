#!/usr/bin/env python

# apps.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.utils import read_json, write_json, get_date_now, ensure_dir, \
    chown_path, run_print_output_error, run_bg, run_cmd
from kano.logging import logger
from kano_profile.paths import apps_dir, xp_file, kanoprofile_dir, \
    app_profiles_file


def get_app_dir(app_name):
    app_dir = os.path.join(apps_dir, app_name)
    return app_dir


def get_app_data_dir(app_name):
    data_str = 'data'
    app_data_dir = os.path.join(get_app_dir(app_name), data_str)
    return app_data_dir


def get_app_state_file(app_name):
    app_state_str = 'state.json'
    app_state_file = os.path.join(get_app_dir(app_name), app_state_str)
    return app_state_file


def load_app_state(app_name):
    app_state_file = get_app_state_file(app_name)
    app_state = read_json(app_state_file)
    if not app_state:
        app_state = dict()
    return app_state


def load_app_state_variable(app_name, variable):
    data = load_app_state(app_name)
    if variable in data:
        return data[variable]


def save_app_state(app_name, data):
    """ Save a state of an application to the user's Kano profile.

        :param app_name: The application that this data are associated with.
        :type app_name: str

        :param data: The data to be stored.
        :type data: dict
    """

    logger.debug('save_app_state {}'.format(app_name))

    app_state_file = get_app_state_file(app_name)
    data['save_date'] = get_date_now()
    ensure_dir(get_app_dir(app_name))
    write_json(app_state_file, data)
    if 'SUDO_USER' in os.environ:
        chown_path(kanoprofile_dir)
        chown_path(apps_dir)
        chown_path(get_app_dir(app_name))
        chown_path(app_state_file)


def save_app_state_variable(app_name, variable, value):
    """ Save a state variable to the user's Kano profile.

        :param app_name: The application that this variable is associated with.
        :type app_name: str
        :param variable: The name of the variable.
        :type data: str
        :param data: The variable data to be stored.
        :type data: any
    """

    msg = 'save_app_state_variable {} {} {}'.format(app_name, variable, value)
    logger.debug(msg)

    data = load_app_state(app_name)
    data[variable] = value

    save_app_state(app_name, data)


def increment_app_state_variable(app_name, variable, value):
    logger.debug(
        'increment_app_state_variable {} {} {}'.format(
            app_name, variable, value))

    data = load_app_state(app_name)
    if variable not in data:
        data[variable] = 0
    data[variable] += value

    save_app_state(app_name, data)


def get_app_list():
    if not os.path.exists(apps_dir):
        return []
    else:
        return [p for p in os.listdir(apps_dir)
                if os.path.isdir(os.path.join(apps_dir, p))]


def get_gamestate_variables(app_name):
    allrules = read_json(xp_file)
    if not allrules:
        return list()

    groups = allrules[app_name]

    for group, rules in groups.iteritems():
        if group == 'multipliers':
            return [str(key) for key in rules.keys()]


def launch_project(app, filename, data_dir, background=False):
    # This is necessary to support the new official names
    # TODO: once the apps have been renamed this will not be necessary
    name_translation = {
        "make-art": "kano-draw",
        "terminal-quest": "linux-story"
    }

    app_tr = name_translation.get(app, app)

    logger.info('launch_project: {} {} {}'.format(app_tr, filename, data_dir))

    app_profiles = read_json(app_profiles_file)

    # XML file with complete pathname
    fullpath = os.path.join(data_dir, filename)

    # Prepare the command line to open the app with the new project
    try:
        cmd = (app_profiles[app_tr]['cmd']
               .format(fullpath=fullpath, filename=filename))
    except KeyError as exc:
        logger.warn(
            "Can't find app '{}' in the app profiles - [{}]"
            .format(app_tr, exc)
        )
        raise ValueError('App "{}" not available'.format(app_tr))

    # Try to load the project if the app is already running, via a signal.
    _, _, rc = run_cmd('/usr/bin/kano-signal launch-share {}'.format(fullpath))
    if rc:
        # Likely the app is not running and the signal could not be sent, so start it now
        logger.warn('Error sending launch signal, starting the app now, rc={}'.format(rc))
        if background:
            run_bg(cmd)
        else:
            _, _, rc = run_print_output_error(cmd)
            return rc
    else:
        logger.info('Sent signal to app: {} to open : {}'.format(app_tr, fullpath))

    return 0


def get_app_xp_for_challenge(app, challenge_no):
    xp_file_json = read_json(xp_file)

    try:
        return xp_file_json[app]['level'][challenge_no]
    except KeyError:
        return 0


def get_all_users():
    existing_users = []
    possible_users = os.listdir("/home")
    for user in possible_users:
        profile_path = os.path.join("/home", user, ".kanoprofile")
        if os.path.exists(profile_path):
            existing_users.append(user)
    return existing_users


def save_app_state_variable_all_users(app, variable, value):
    if os.environ['LOGNAME'] != 'root':
        logger.error("Error: save_app_state_variable_all_users must be executed with root privileges")
        return

    users = get_all_users()

    for user in users:
        dir_path = os.path.join(
            "/home", user, ".kanoprofile", "apps", app
        )
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            chown_path(dir_path, user, user)

        state_path = os.path.join(dir_path, "state.json")
        data = {variable: value}
        data['save_date'] = get_date_now()
        write_json(state_path, data)
        chown_path(state_path, user, user)
