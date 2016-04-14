#!/usr/bin/env python

# badges.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from __future__ import division

import os
import json
import itertools
from copy import deepcopy

from kano.logging import logger
from kano.utils import read_json, is_gui, run_bg
from .paths import xp_file, levels_file, rules_dir, bin_dir, \
    app_profiles_file, online_badges_dir, online_badges_file
from .apps import load_app_state, get_app_list, save_app_state
from .quests import Quests


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

            if group == 'groups':
                # Iterate over the groups of the local profile
                groups_item_iter = appstate.get('groups', {}).iteritems
                for grp_name, grp_obj in groups_item_iter():
                    level_achieved = int(
                        appstate['groups'][grp_name]['challengeNo']
                    )
                    for level, value in rules.get(grp_name, {}).iteritems():
                        level = int(level)
                        value = int(value)

                        if level <= level_achieved:
                            points += value
    qm = Quests()
    return int(points) + qm.evaluate_xp()


def get_group_progress(group_profile):
    if 'challengeNo' not in group_profile:
        return 0

    return group_profile['challengeNo']


def calculate_app_progress(app_name):
    app_profile = load_app_state(app_name)
    progress = 0

    if 'groups' in app_profile and app_profile['groups']:
        groups_profile = app_profile['groups']
        for group in groups_profile:
            progress += get_group_progress(groups_profile[group])

        return progress

    if 'level' in app_profile and app_profile['level']:
        progress = app_profile['level']

    return progress


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


class BadgeCalc(object):
    def __init__(self):
        self._app_profiles = read_json(app_profiles_file)
        if not self._app_profiles:
            logger.error('Error reading app_profiles.json')
            raise RuntimeError("Couldn't read app profiles")

        self._app_list = get_app_list() + ['computed']
        self._app_state = dict()
        for app in self._app_list:
            self._app_state[app] = load_app_state(app)

        self._app_state.setdefault('computed', dict())['kano_level'] = \
            calculate_kano_level()[0]

        self._all_rules = load_badge_rules()
        self._calculated_badges = {}

    def _parse_target_variable(self, variable):
        return variable.split('.')

    def _get_variable(self, app, target_keys):
        if target_keys == ['level']:
            return calculate_app_progress(app)

        ret_val = None

        try:
            ret_val = self._app_state[app]

            for key in target_keys:
                ret_val = ret_val[key]
        except (TypeError, KeyError):
            ret_val = None

        return ret_val

    def _are_each_greater(self, targets):
        for target in targets:
            app = target[0]
            attr_list = self._parse_target_variable(target[1])
            threshold_value = target[2]

            local_value = self._get_variable(app, attr_list)

            if local_value is None:
                return False

            if attr_list[-1] == 'level' and threshold_value == -1:
                threshold_value = self._app_profiles[app]['max_level']

            if local_value < threshold_value:
                return False

        return True

    def _is_sum_greater(self, targets, threshold_value):
        total = 0

        for target in targets:
            app = target[0]
            attr_list = self._parse_target_variable(target[1])

            local_value = self._get_variable(app, attr_list)

            if local_value:
                total += float(local_value)

        return total >= threshold_value

    def _evaluate_rules(self, rules):
        """ Evaluates the rules and returns whether the badge has been unlocked
        :param rules: The category whose z-index will be returned
        :returns: True or False if the badge has been achieved. If the rules
                  are malformed it returns None
        :rtype: Boolean or NoneType
        """

        warn_template = "Malformed badge rules, missing '{}' - [{}]"
        req_fields = [
            'operation',
            'targets'
        ]

        for field in req_fields:
            if field not in rules:
                logger.warn(warn_template.format(field, rules))
                return None

        if rules['operation'] == 'each_greater':
            return self._are_each_greater(rules['targets'])

        if rules['operation'] == 'sum_greater':
            if 'value' not in rules:
                logger.warn(warn_template.format('value', rules))
                return None

            return self._is_sum_greater(rules['targets'], rules['value'])

        return None

    @staticmethod
    def is_push_back(item):
        """ Tells us if a rule is of type push_back i.e. to be calculated at
        the end
        :param item: A container with the rules dict embedded
        :type item: tuple with dict in position [1]
        :returns: True if the rule calculation is to be delayed until non push
                  back badges are evaluated
        :rtype: Boolean
        """
        rules = item[1]
        return 'push_back' in rules and rules['push_back'] is True

    def _do_calculate(self, calculate_only_pushed_back):
        """ Perform the evaluation of the badge unlocking conditions. It stores
        the results in self._calculated_badges
        the end
        :param calculate_only_pushed_back: Only calculate 'push_back' type
                                           badges
        :type calculate_only_pushed_back: Boolean
        """
        for category, subcats in self._all_rules.iteritems():
            for subcat, items in subcats.iteritems():
                if calculate_only_pushed_back:
                    filter_fn = itertools.ifilter
                else:
                    filter_fn = itertools.ifilterfalse

                it = filter_fn(self.is_push_back, items.iteritems())

                for item, rules in it:
                    achieved = self._evaluate_rules(rules)
                    if achieved is None:
                        continue

                    calc_badge = self._calculated_badges.setdefault(
                        category,
                        {}
                    )
                    calc_subcat = calc_badge.setdefault(subcat, {})
                    calc_subcat[item] = self._all_rules[category][subcat][item]
                    calc_subcat[item]['achieved'] = achieved

    def count_offline_badges(self):
        count = 0
        # Only iterate over badges
        iter_badges = itertools.ifilter(lambda k: k[0] == 'badges',
                                        self._calculated_badges.iteritems())
        for category, subcats in iter_badges:
            # Only get the online badges
            iter_subcats = itertools.ifilter(lambda k: k[0] != 'online',
                                             subcats.iteritems())
            for subcat, items in iter_subcats:
                # Count achieved
                achieved_iter = itertools.ifilter(lambda k: k['achieved'],
                                                  items.itervalues())
                count += sum(1 for b in achieved_iter)
        return count

    @property
    def calculated_badges(self):
        # Calculate badges/environments
        self._do_calculate(False)

        # count offline badges
        self._app_state['computed']['num_offline_badges'] = \
            self.count_offline_badges()

        # Calculate badges marked as push_back (those for which the num of
        # offline badges needs to have been calculated)
        self._do_calculate(True)

        # Inject badges from quests to the dict
        qm = Quests()
        self._calculated_badges['badges']['quests'] = qm.evaluate_badges()

        return deepcopy(self._calculated_badges)


def calculate_badges():
    ret_v = {}
    try:
        badge_c = BadgeCalc()
        ret_v = badge_c.calculated_badges
    except KeyError as exc:
        logger.error('Configuration missing some value: [{}]'.format(exc))
    except RuntimeError as exc:
        logger.error('Error while trying to calculate badges [{}]'.format(exc))

    return ret_v


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
    try:
        f = open(online_badges_file, "r")
    except IOError as e:
        logger.error(
            'Error opening badges file: {}'.format(e))
    else:
        with f:
            online_badges = json.load(f)

    return online_badges


def write_notifications(filename, notifications):
    # write badge lines to the fifo. Ignore timeouts
    # and the other end not having the fifo open.
    try:
        fifo = os.open(
            filename,
            os.O_WRONLY | os.O_NONBLOCK | os.O_APPEND
        )
    except OSError:
        # probably the other end doesn't have the fifo open
        return
    try:
        for notification in notifications:
            if len(notification) > 0:
                logger.debug(
                    "Showing the {} notification".format(notification)
                )
                os.write(fifo,'{}\n'.format(notification))
    finally:
        os.close(fifo)

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
        # Open the fifo in append mode, as if it is not
        # present, notifications are queued in a flat file
        notifications = (new_level_str + ' ' + new_items_str).split(' ')
        
        # Write  to both the dashboard and the desktop widget
        f1 = os.path.join(os.path.expanduser('~'), '.kano-notifications.fifo')
        f2 = os.path.join(os.path.expanduser('~'), '.kano-notifications-desktop.fifo')
        write_notifications(f1, notifications)
        write_notifications(f2, notifications)

    cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
    run_bg(cmd)


def save_app_state_variable_with_dialog(app_name, variable, value):
    logger.debug(
        'save_app_state_variable_with_dialog {} {} {}'
        .format(app_name, variable, value)
    )

    data = load_app_state(app_name)
    data[variable] = value

    save_app_state_with_dialog(app_name, data)


def update_upwards_with_dialog(app_name, variable, value):
    """ Only update a numeric value in the profile if the one given is higher.
    Useful for highscores, etc

    :param app_name: The application that this variable is associated with.
    :type app_name: str

    :param variable: The name of the variable.
    :type data: str

    :param value: The value to be stored if it is higher that the one already
                  stored
    :type data: numeric
    """
    msg = "update_increasingly_with_dialog {} {} {}".format(
        app_name, variable, value
    )
    logger.debug(msg)
    data = load_app_state(app_name)
    if data.get(variable, 0) < value:
        data[variable] = value

        save_app_state_with_dialog(app_name, data)


def increment_app_state_variable_with_dialog(app_name, variable, value):
    logger.debug(
        'increment_app_state_variable_with_dialog {} {} {}'
        .format(app_name, variable, value)
    )

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
            logger.error(
                'no rule files in subfolder: {}'.format(folder_fullpath)
            )
            return

        for rule_file in rule_files:
            rule_file_fullpath = os.path.join(folder_fullpath, rule_file)
            if os.path.splitext(rule_file_fullpath)[1] != '.json':
                logger.debug(
                    'Skipping over non json {}'.format(rule_file_fullpath)
                )
                continue
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
