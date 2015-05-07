#!/usr/bin/env python

# print_needed_variables.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano_profile.badges import load_badge_rules
from kano.utils import write_json, uniqify_list

all_rules = load_badge_rules()

variables_needed = dict()

for category, subcats in all_rules.iteritems():
    for subcat, items in subcats.iteritems():
        for item, rules in items.iteritems():
            targets = rules['targets']
            for target in targets:
                app = target[0]
                variable = target[1]
                variables_needed.setdefault(app, list()).append(variable)

for key in variables_needed.iterkeys():
    variables_needed[key] = uniqify_list(variables_needed[key])


write_json('variables_needed.json', variables_needed, False)
