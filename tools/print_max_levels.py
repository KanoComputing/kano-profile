#!/usr/bin/env python

# print_max_levels.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano_profile.badges import load_badge_rules
from kano.utils import uniqify_list

all_rules = load_badge_rules()
max_variables = list()

for category, subcats in all_rules.iteritems():
    for subcat, items in subcats.iteritems():
        for item, rules in items.iteritems():
            if rules['operation'] != 'each_greater':
                continue

            targets = rules['targets']
            for target in targets:
                app, variable, value = target
                if value == -1:
                    max_variables.append((app, variable))
                    print category, subcat, item, app, variable, value

print
max_variables = sorted(uniqify_list(max_variables))
for app, variable in max_variables:
    print app, variable
