#!/usr/bin/env python

# kano.profile
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from __future__ import division

import sys
import os
import json

from kano.utils import read_file_contents, get_cpu_id, get_mac_address, \
    get_date_now, ensure_dir, get_user, get_home_by_username, is_gui


def load_profile():
    data = read_json(profile_file)
    if not data:
        data = dict()

    if 'username_linux' not in data:
        data['username_linux'] = linux_user

    if 'email' not in data and get_email_from_disk():
        data['email'] = get_email_from_disk()

    if 'cpu_id' not in data and get_cpu_id():
        data['device_id'] = get_cpu_id()

    if 'mac_addr' not in data and get_mac_address():
        data['mac_addr'] = get_mac_address()

    return data


def save_profile(data):
    data['last_save_date'] = get_date_now()
    write_json(profile_file, data)


def get_email_from_disk():
    kano_email_file = os.path.join(home_directory, '.useremail')
    return read_file_contents(kano_email_file)


def get_app_dir(app_name):
    app_dir = os.path.join(apps_dir, app_name)
    ensure_dir(app_dir)
    return app_dir


def get_app_data_dir(app_name):
    data_str = 'data'
    app_data_dir = os.path.join(get_app_dir(app_name), data_str)
    ensure_dir(app_data_dir)
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
    if is_unlocked():
        data['level'] = 999
    if variable in data:
        return data[variable]


def save_app_state(app_name, data):
    if is_unlocked():
        old_app_state = load_app_state(app_name)
        data['level'] = old_app_state['level']

    app_state_file = get_app_state_file(app_name)
    data['last_save_date'] = get_date_now()
    write_json(app_state_file, data)


def save_app_state_variable(app_name, variable, value):
    if is_unlocked() and variable == 'level':
        return
    data = load_app_state(app_name)
    data[variable] = value
    save_app_state(app_name, data)


def read_json(filepath, print_warning=False):
    try:
        return json.loads(read_file_contents(filepath))
    except Exception:
        if print_warning:
            print "Problem with opening: {}".format(filepath)


def write_json(filepath, data):
    with open(filepath, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def calculate_xp():
    allrules = read_json(xp_file)
    if not allrules:
        return -1

    points = 0

    for app, groups in allrules.iteritems():
        appstate = load_app_state(app)
        if not appstate:
            continue

        for group, rules in groups.iteritems():
            # calculating points based on level
            if group == 'level' and 'level' in appstate:
                maxlevel = int(appstate['level'])

                for level, value in rules.iteritems():
                    level = int(level)
                    value = int(value)

                    if level <= maxlevel:
                        points += value

            # calculating points based on multipliers
            if group == 'multipliers':
                for thing, value in rules.iteritems():
                    value = float(value)
                    if thing in appstate:
                        points += value * appstate[thing]

    return int(points)


def calculate_kano_level():
    level_rules = read_json(levels_file)
    if not level_rules:
        return -1, 0

    max_level = max([int(n) for n in level_rules.keys()])
    xp_now = calculate_xp()

    for level in xrange(1, max_level + 1):
        level_min = level_rules[str(level)]

        if level != max_level:
            level_max = level_rules[str(level + 1)] - 1
        else:
            level_max = float("inf")

        if level_min <= xp_now <= level_max:
            reached_level = level
            reached_percentage = (xp_now - level_min) / (level_max + 1 - level_min)

            return int(reached_level), reached_percentage


def get_app_list(include_empty=False):
    apps = []
    allrules = read_json(xp_file)
    if not allrules:
        return apps

    for app, groups in allrules.iteritems():
        appstate = load_app_state(app)
        if not appstate and not include_empty:
            continue
        else:
            apps.append(app)

    return apps


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


# start
if __name__ == "__main__":
    sys.exit("Should be imported as module")

# getting linux variables
linux_user = get_user()
home_directory = get_home_by_username(linux_user)
module_file = os.path.realpath(__file__)
module_dir = os.path.dirname(module_file)

# constructing paths of directories, files
kanoprofile_dir_str = '.kanoprofile'
kanoprofile_dir = os.path.join(home_directory, kanoprofile_dir_str)

profile_dir_str = 'profile'
profile_dir = os.path.join(kanoprofile_dir, profile_dir_str)

apps_dir_str = 'apps'
apps_dir = os.path.join(kanoprofile_dir, apps_dir_str)

profile_file_str = 'profile.json'
profile_file = os.path.join(profile_dir, profile_file_str)

xp_file = '/usr/share/kano-profile/rules/xp.json'
levels_file = '/usr/share/kano-profile/rules/levels.json'

is_gui = is_gui()

if not os.path.exists(profile_file):
    profile = load_profile()
    ensure_dir(profile_dir)
    save_profile(profile)


