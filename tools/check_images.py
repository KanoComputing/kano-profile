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

from kano.profile.badges import load_badge_rules
from kano_profile_gui.paths import image_dir


all_rules = load_badge_rules()

for category, subcats in all_rules.iteritems():
    for subcat, items in subcats.iteritems():
        path = os.path.join(image_dir, category, 'originals', subcat)

        existing_items = os.listdir(path)
        needed_items = ['{}.png'.format(f) for f in items.keys()]

        if sorted(existing_items) != sorted(needed_items):
            print existing_items
            print needed_items
            print
