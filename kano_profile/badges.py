#!/usr/bin/env python

# badges.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from __future__ import division

import os
import json

from kano.logging import logger
from kano.utils import read_json, is_gui, is_running, run_bg
from .paths import xp_file, levels_file, rules_dir, bin_dir, \
    app_profiles_file, online_badges_dir, online_badges_file
from .apps import load_app_state, get_app_list, save_app_state


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
    '''
    Calculates the current level of the user
    Returns: level, percentage and current xp
    '''
    level_rules = read_json(levels_file)
    if not level_rules:
        return -1, 0, 0

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

            return int(reached_level), reached_percentage, xp_now


def calculate_min_current_max_xp():
    level_rules = read_json(levels_file)
    if not level_rules:
        return -1, 0

    max_level = max([int(n) for n in level_rules.keys()])
    xp_now = calculate_xp()

    level_min = 0
    level_max = 0

    for level in xrange(1, max_level + 1):
        level_min = level_rules[str(level)]

        if level != max_level:
            level_max = level_rules[str(level + 1)]
        else:
            level_max = float("inf")

        if level_min <= xp_now <= level_max:
            return level_min, xp_now, level_max


def calculate_badges():
    # helper function to calculate operations
    def do_calculate(select_push_back):
        for category, subcats in all_rules.iteritems():
            for subcat, items in subcats.iteritems():
                for item, rules in items.iteritems():
                    target_pushback = 'push_back' in rules and rules['push_back'] is True
                    if target_pushback != select_push_back:
                        continue

                    if rules['operation'] == 'each_greater':
                        achieved = True
                        for target in rules['targets']:
                            app = target[0]
                            variable = target[1]
                            value = target[2]

                            if variable == 'level' and value == -1:
                                value = app_profiles[app]['max_level']
                            if app not in app_list or variable not in app_state[app]:
                                achieved = False
                                break
                            achieved &= app_state[app][variable] >= value

                    elif rules['operation'] == 'sum_greater':
                        sum = 0
                        for target in rules['targets']:
                            app = target[0]
                            variable = target[1]

                            if app not in app_list or variable not in app_state[app]:
                                continue

                            sum += float(app_state[app][variable])

                        achieved = sum >= rules['value']

                    else:
                        continue

                    calculated_badges.setdefault(category, dict()).setdefault(subcat, dict())[item] \
                        = all_rules[category][subcat][item]
                    calculated_badges[category][subcat][item]['achieved'] = achieved

    def count_offline_badges():
        count = 0
        for category, subcats in calculated_badges.iteritems():
            for subcat, items in subcats.iteritems():
                for item, rules in items.iteritems():
                    if category == 'badges' and subcat != 'online' and rules['achieved']:
                        count += 1
        return count

    app_profiles = read_json(app_profiles_file)
    if not app_profiles:
        logger.error('Error reading app_profiles.json')

    app_list = get_app_list() + ['computed']
    app_state = dict()
    for app in app_list:
        app_state[app] = load_app_state(app)

    app_state.setdefault('computed', dict())['kano_level'] = calculate_kano_level()[0]

    all_rules = load_badge_rules()
    calculated_badges = dict()

    # normal ones
    do_calculate(False)

    # count offline badges
    app_state['computed']['num_offline_badges'] = count_offline_badges()

    # add pushed back ones
    do_calculate(True)

    return calculated_badges


def compare_badges_dict(old, new):
    if old == new:
        return []
    changes = dict()

    for category, subcats in new.iteritems():
        for subcat, items in subcats.iteritems():
            for item, rules in items.iteritems():
                try:
                    if old[category][subcat][item]['achieved'] is False and \
                       new[category][subcat][item]['achieved'] is True:
                        changes.setdefault(category, dict()).setdefault(subcat, dict())[item] \
                            = new[category][subcat][item]
                except Exception:
                    pass
    return changes


def load_online_badges():
    if not os.path.isdir(online_badges_dir):
        return {}

    online_badges = {}
    with open(online_badges_file, "r") as f:
        online_badges = json.load(f)

    return online_badges


def save_app_state_with_dialog(app_name, data):
    logger.debug('save_app_state_with_dialog {}'.format(app_name))

    old_level, _, old_xp = calculate_kano_level()
    old_badges = calculate_badges()

    save_app_state(app_name, data)

    new_level, _, new_xp = calculate_kano_level()
    new_badges = calculate_badges()

    # TODO: This function needs a bit of refactoring in the future
    # The notifications no longer need to be concatenated to a string

    # new level
    new_level_str = ''
    if old_level != new_level:
        new_level_str = 'level:{}'.format(new_level)

        # A new level has been reached, update the desktop profile icon
        if os.path.exists('/usr/bin/kdesk') and not is_running('kano-sync'):
            logger.info('refreshing kdesk due to new experience level')
            run_bg('kdesk -a profile')

    # new items
    new_items_str = ''
    badge_changes = compare_badges_dict(old_badges, new_badges)
    if badge_changes:
        for category, subcats in badge_changes.iteritems():
            for subcat, items in subcats.iteritems():
                for item, rules in items.iteritems():
                    new_items_str += ' {}:{}:{}'.format(category, subcat, item)

    # Check if XP has changed, if so play sound in the backgrond
    if old_xp != new_xp:
        sound_cmd = 'aplay /usr/share/kano-media/sounds/kano_xp.wav > /dev/null 2>&1 &'
        run_bg(sound_cmd)

    if not new_level_str and not new_items_str:
        return

    if is_gui():
        with open(os.path.join(os.path.expanduser('~'), '.kano-notifications.fifo'), 'w') as fifo:
            for notification in (new_level_str + ' ' + new_items_str).split(' '):
                if len(notification) > 0:
                    logger.debug("Showing the {} notification".format(notification))
                    fifo.write('{}\n'.format(notification))

    cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
    run_bg(cmd)


def save_app_state_variable_with_dialog(app_name, variable, value):
    logger.debug('save_app_state_variable_with_dialog {} {} {}'.format(app_name, variable, value))

    data = load_app_state(app_name)
    data[variable] = value

    save_app_state_with_dialog(app_name, data)


def increment_app_state_variable_with_dialog(app_name, variable, value):
    logger.debug('increment_app_state_variable_with_dialog {} {} {}'.format(app_name, variable, value))

    data = load_app_state(app_name)
    if variable not in data:
        data[variable] = 0
    data[variable] += value

    save_app_state_with_dialog(app_name, data)


def load_badge_rules():
    if not os.path.exists(rules_dir):
        logger.error('rules dir missing')
        return

    merged_rules = dict()
    subfolders = ['badges', 'environments']
    for folder in subfolders:
        folder_fullpath = os.path.join(rules_dir, folder)
        if not os.path.exists(folder_fullpath):
            logger.error('rules subfolder missing: {}'.format(folder_fullpath))
            return

        rule_files = os.listdir(folder_fullpath)
        if not rule_files:
            logger.error('no rule files in subfolder: {}'.format(folder_fullpath))
            return

        for rule_file in rule_files:
            rule_file_fullpath = os.path.join(folder_fullpath, rule_file)
            rule_data = read_json(rule_file_fullpath)
            if not rule_data:
                logger.error('rule file empty: {}'.format(rule_file_fullpath))
                continue

            category = folder
            subcategory = rule_file.split('.')[0]

            merged_rules.setdefault(category, dict())[subcategory] = rule_data
    return merged_rules


def count_completed_challenges():
    allrules = read_json(xp_file)
    if not allrules:
        return -1

    completed_challenges = 0

    for app, groups in allrules.iteritems():
        appstate = load_app_state(app)
        try:
            completed_challenges += int(appstate['level'])
        except Exception:
            pass

    return completed_challenges


def count_badges():
    all_badges = calculate_badges()

    locked = {
        'badges': 0,
        'environments': 0,
    }

    unlocked = {
        'badges': 0,
        'environments': 0,
    }

    for category, subcats in all_badges.iteritems():
        for subcat, items in subcats.iteritems():
            for item, rules in items.iteritems():
                if rules['achieved']:
                    unlocked[category] += 1
                else:
                    locked[category] += 1

    return dict(unlocked), dict(locked)


def count_stat(key):
    allrules = read_json(xp_file)
    if not allrules:
        return -1

    count = 0

    for app, _ in allrules.iteritems():
        appstate = load_app_state(app)
        try:
            count += int(appstate[key])
        except Exception:
            pass

    return count


def count_number_of_blocks():
    return count_stat('blocks_created')


def count_number_of_shares():
    return count_stat('shared')


def count_lines_of_code():
    return count_stat('lines_of_code')
