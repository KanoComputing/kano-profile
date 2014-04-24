#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from __future__ import division

import os

from ..utils import read_json, is_gui, run_cmd
from .paths import xp_file, levels_file, badges_folder, bin_dir
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

    # helper function to calculate operations
    def do_calculate(select_push_back):
        for category, items in rules.iteritems():
            for item, rule in items.iteritems():
                target_pushback = 'push_back' in rule and rule['push_back'] is True
                if target_pushback != select_push_back:
                    continue

                if rule['operation'] == 'stat_gta':
                    achieved = True
                    for target in rule['targets']:
                        app = target[0]
                        variable = target[1]
                        value = target[2]

                        if app not in app_list or variable not in app_state[app]:
                            achieved = False
                            break
                        achieved &= app_state[app][variable] >= value
                    badges.setdefault(category, dict())[item] = achieved

                elif rule['operation'] == 'stat_sum_gt':
                    sum = 0
                    for target in rule['targets']:
                        app = target[0]
                        variable = target[1]

                        if app not in app_list or variable not in app_state[app]:
                            continue

                        sum += float(app_state[app][variable])

                    achieved = sum >= rule['value']
                    badges.setdefault(category, dict())[item] = achieved

                else:
                    print 'unknown uperation {}'.format(rule['operation'])

    def count_offline_badges():
        count = 0
        for category, items in badges.iteritems():
            for item, value in items.iteritems():
                if value:
                    count += 1
        return count

    if not os.path.exists(badges_folder):
        print 'badge rules folder missing'
        return

    rule_files = os.path.listdir(badges_folder)
    if not rule_files:
        print 'No rule files!'
        return


    # rules = read_json(badges_file)
    # if not rules:
    #     return

    # app_list = get_app_list() + ['kano-world']
    # app_state = dict()
    # for app in app_list:
    #     app_state[app] = load_app_state(app)

    # # special app: kanoprofile
    # profile_state = dict()
    # profile_state['xp'] = calculate_xp()
    # profile_state['level'], _ = calculate_kano_level()
    # app_state['kano-world'] = profile_state

    # badges = dict()

    # # normal ones
    # do_calculate(False)

    # # count offline badges
    # app_state['kano-world']['num_offline_badges'] = count_offline_badges()

    # # add pushed back ones
    # do_calculate(True)

    # return badges


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


def save_app_state_with_dialog(app_name, data):
    old_level, _ = calculate_kano_level()
    old_badges = calculate_badges()

    save_app_state(app_name, data)

    new_level, _ = calculate_kano_level()
    new_badges = calculate_badges()

    # new level dialog
    if is_gui() and old_level != new_level:
        cmd = '{bin_dir}/kano-profile-new-badges-dialog newlevel "{new_level}"'.format(bin_dir=bin_dir, new_level=new_level)
        run_cmd(cmd)

    # new badges dialog
    badge_changes = compare_badges_dict(old_badges, new_badges)
    if is_gui() and badge_changes:
        changes_list = list()
        for group, items in badge_changes.iteritems():
            for item in items:
                changes_list.append((group, item))

        chg_str = ' '.join(['{}:{}'.format(group, item) for group, item in changes_list])
        cmd = '{bin_dir}/kano-profile-new-badges-dialog newbadges {chg_str}'.format(bin_dir=bin_dir, chg_str=chg_str)
        run_cmd(cmd)


def save_app_state_variable_with_dialog(app_name, variable, value):
    if is_unlocked() and variable == 'level':
        return
    data = load_app_state(app_name)
    data[variable] = value
    save_app_state_with_dialog(app_name, data)








