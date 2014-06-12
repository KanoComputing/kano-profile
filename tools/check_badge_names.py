#!/usr/bin/env python

# check_badge_names.py
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
from slugify import slugify

all_rules = load_badge_rules()

ok = True
for category, subcats in all_rules.iteritems():
    for subcat, items in subcats.iteritems():
        for item, rules in items.iteritems():
            slug = slugify(rules['title']).replace('-', '_')
            if item != slug:
                print item, slug
                ok = False


if ok:
    print 'All names are OK'


