#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from __future__ import division

import json

from ..utils import read_json, get_date_now, is_gui, run_cmd
from .paths import xp_file, levels_file, badges_file, bin_dir
from .apps import load_app_state, get_app_list, save_app_state
from .profile import is_unlocked


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


def calculate_badges():
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


def save_app_state_with_dialog(app_name, data):
    if is_unlocked():
        data['level'] = load_app_state(app_name)['level']

    data['last_save_date'] = get_date_now()

    old_level, _ = calculate_kano_level()
    old_badges = calculate_badges()

    save_app_state(app_name, data)

    new_level, _ = calculate_kano_level()
    new_badges = calculate_badges()

    # New level dialog
    if is_gui() and old_level != new_level:
        cmd = '{bin_dir}/kano-profile-dialog newlevel "{new_level}"'.format(bin_dir=bin_dir, new_level=new_level)
        run_cmd(cmd)

    badge_changes = compare_badges_dict(old_badges, new_badges)
    if is_gui() and badge_changes:
        cmd = '{bin_dir}/kano-profile-dialog newbadges "{json}"'.format(bin_dir=bin_dir, json=json.dumps(badge_changes))
        run_cmd(cmd)


def compare_badges_dict(old, new):
    if old == new:
        return []
    changes = dict()
    for group, items in new.iteritems():
        for item, value in items.iteritems():
            if group in old and item in old[group] and \
               old[group][item] is False and value is True:
                changes.setdefault(group, []).append(item)
    return changes








