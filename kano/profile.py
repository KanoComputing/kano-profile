#!/usr/bin/env python

# kano.profile
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from __future__ import division

import sys
import os
import grp
import json
import kano.utils as ku


def load_profile():
    data = read_json(profile_file)
    if not data:
        data = dict()

    if 'username_linux' not in data:
        data['username_linux'] = linux_user

    if 'email' not in data and get_email_from_disk():
        data['email'] = get_email_from_disk()

    if 'device_id' not in data and ku.get_device_id():
        data['device_id'] = ku.get_device_id()

    if 'mac_addr' not in data and ku.get_mac_address():
        data['mac_addr'] = ku.get_mac_address()

    return data


def save_profile(data):
    data['last_save_date'] = ku.get_date_now()
    write_json(profile_file, data)


def get_email_from_disk():
    kano_email_file = os.path.join(home_directory, '.useremail')
    return ku.read_file_contents(kano_email_file)


def get_app_dir(app_name):
    app_dir = os.path.join(apps_dir, app_name)
    ku.ensure_dir(app_dir)
    return app_dir


def get_app_data_dir(app_name):
    data_str = 'data'
    app_data_dir = os.path.join(get_app_dir(app_name), data_str)
    ku.ensure_dir(app_data_dir)
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
    if is_unlocked():
        old_app_state = load_app_state(app_name)
        data['level'] = old_app_state['level']

    app_state_file = get_app_state_file(app_name)
    data['last_save_date'] = ku.get_date_now()

    old_level, _ = calculate_kano_level()
    old_badges = calculate_badges_swags('badges')
    old_swags = calculate_badges_swags('swags')

    write_json(app_state_file, data)

    new_level, _ = calculate_kano_level()
    new_badges = calculate_badges_swags('badges')
    new_swags = calculate_badges_swags('swags')

    # New level dialog
    if is_gui and old_level != new_level:
        cmd = 'kano-profile-dialog newlevel {}'.format(new_level)
        ku.run_cmd(cmd)

    # New badges dialog
    if is_gui and old_badges != new_badges:
        chg_badges = []
        for badge in old_badges:
            if old_badges[badge] is False and new_badges[badge] is True:
                chg_badges.append(badge)
        cmd = 'kano-profile-dialog newbadges {}'.format(' '.join(chg_badges))
        ku.run_cmd(cmd)

    # New swags dialog
    if is_gui and old_swags != new_swags:
        chg_swags = []
        for swag in old_swags:
            if old_swags[swag] is False and new_swags[swag] is True:
                chg_swags.append(swag)
        cmd = 'kano-profile-dialog newswags {}'.format(' '.join(chg_swags))
        ku.run_cmd(cmd)


def save_app_state_variable(app_name, variable, value):
    if is_unlocked() and variable == 'level':
        return
    data = load_app_state(app_name)
    data[variable] = value
    save_app_state(app_name, data)


def read_json(filepath, print_warning=False):
    try:
        return json.loads(ku.read_file_contents(filepath))
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


def calculate_badges_swags():
    rules = read_json(badges_file)
    if not rules:
        return

    kano_level, _ = calculate_kano_level()
    app_list = get_app_list()
    app_state = dict()
    for app in app_list:
        app_state[app] = load_app_state(app)

    badges = dict()
    for category, items in rules.iteritems():
        for name, rule in items.iteritems():
            if rule['operation'] == 'stat_gta':
                achieved = True
                for target in rule['targets']:
                    app = target[0]
                    variable = target[1]
                    value = target[2]

                    if app not in app_list or variable not in app_state[app]:
                        achieved = False
                        continue
                    achieved &= app_state[app][variable] >= value
                badges.setdefault(category, dict())[name] = achieved

            elif rule['operation'] == 'stat_sum_gt':
                sum = 0
                for target in rule['targets']:
                    app = target[0]
                    variable = target[1]

                    if app not in app_list or variable not in app_state[app]:
                        continue

                    sum += float(app_state[app][variable])

                achieved = sum >= rule['value']
                badges.setdefault(category, dict())[name] = achieved

            else:
                print 'unknown uperation {}'.format(rule['operation'])

    return badges


def get_gamestate_variables(app_name):
    allrules = read_json(xp_file)
    if not allrules:
        return list()

    groups = allrules[app_name]

    for group, rules in groups.iteritems():
        if group == 'multipliers':
            return [str(key) for key in rules.keys()]


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
    return load_profile()['unlocked']


# start
if __name__ == "__main__":
    sys.exit("Should be imported as module")

# checking kanousers group
try:
    kanogrp = grp.getgrnam('kanousers')
    kanomembers = kanogrp.gr_mem
except KeyError:
    sys.exit("kanousers group doesn't exist\nrun 'groupadd kanousers' first")

# getting linux variables
linux_user = ku.get_user()
home_directory = ku.get_home_by_username(linux_user)
module_file = os.path.realpath(__file__)
module_dir = os.path.dirname(module_file)

# check if run under kanouser (or sudo-ed kanouser)
if linux_user not in kanomembers:
    sys.exit("You are not member of kanousers group\nrun `usermod -a -G kanousers {}` first".format(linux_user))

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
badges_file = '/usr/share/kano-profile/rules/badges.json'

is_gui = ku.is_gui()

if not os.path.exists(profile_file):
    profile = load_profile()
    ku.ensure_dir(profile_dir)
    save_profile(profile)


