#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.utils import read_json, write_json, get_date_now, ensure_dir
from .paths import apps_dir, xp_file
from .profile import is_unlocked


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
    if is_unlocked():
        data['level'] = 999
    if variable in data:
        return data[variable]


def save_app_state(app_name, data):
    if is_unlocked():
        data['level'] = load_app_state(app_name)['level']

    app_state_file = get_app_state_file(app_name)
    data['save_date'] = get_date_now()
    ensure_dir(get_app_dir(app_name))
    write_json(app_state_file, data)


def save_app_state_variable(app_name, variable, value):
    if is_unlocked() and variable == 'level':
        return
    data = load_app_state(app_name)
    data[variable] = value
    save_app_state(app_name, data)


def get_app_list():
    if not os.path.exists(apps_dir):
        return []
    else:
        return [p for p in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, p))]


def get_gamestate_variables(app_name):
    allrules = read_json(xp_file)
    if not allrules:
        return list()

    groups = allrules[app_name]

    for group, rules in groups.iteritems():
        if group == 'multipliers':
            return [str(key) for key in rules.keys()]
