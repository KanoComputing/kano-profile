#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano_profile_gui.paths import css_dir
from kano_login import home, login
from kano_login.components import top_bar
from kano.world.functions import is_registered, login_using_token



from slugify import slugify



def test_badge_rules():
    merged_rules = load_badge_rules()

    properties = dict()
    max_values = dict()

    for category, items in merged_rules.iteritems():
        for badge, badge_rules in items.iteritems():
            for target in badge_rules['targets']:
                if badge_rules['operation'] == 'stat_sum_gt':
                    profile, variable = target
                    value = badge_rules['value']
                elif badge_rules['operation'] == 'stat_gta':
                    profile, variable, value = target

                properties.setdefault(profile, set()).add(variable)

                if value == -1:
                    # print rule_file, badge, profile, variable, value
                    max_values.setdefault(profile, set()).add(variable)

            # check if name == slugified title
            if True:
                slug = slugify(badge_rules['title']).replace('-', '_')
                if badge != slug:
                    print category, badge, slug

            # print titles
            if False:
                print badge_rules['title']

    # print max_values
    if False:
        for category, items in max_values.iteritems():
            print category, '-', ' '.join(items)

    # print all properties
    if False:
        for category, items in properties.iteritems():
            print category, '-', ' '.join(items)

    # test achieved
    if False:
        calculated_badges = calculate_badges()
        for category, items in calculated_badges.iteritems():
            for badge, properties in items.iteritems():
                if not 'achieved' in properties:
                    print category, badge, properties
