#!/usr/bin/env python

# check_images.py
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
from kano_profile_gui.paths import image_dir
from kano.utils import uniqify_list


all_rules = load_badge_rules()

ok = True
for category, subcats in all_rules.iteritems():
    for subcat, items in subcats.iteritems():
        path = os.path.join(image_dir, category, 'originals', subcat)

        existing_items = sorted([f for f in os.listdir(path)])
        needed_items_images = ['{}.png'.format(f) for f in items.keys()]
        needed_items_locked = ['{}_locked.png'.format(f) for f in items.keys()]
        needed_items_circular = ['{}_circular.png'.format(f) for f in items.keys()]
        needed_items_white_circular = ['{}_white_circular.png'.format(f) for f in items.keys()]
        needed_items_levelup = ['{}_levelup.png'.format(f) for f in items.keys()]

        if category == 'avatars':
            needed_items_levelup = uniqify_list(['{}_levelup.png'.format(f[:-2]) for f in items.keys()])
            needed_items = needed_items_images + needed_items_locked + needed_items_circular + \
                needed_items_levelup + needed_items_white_circular

        if category == 'badges':
            needed_items = needed_items_images + needed_items_locked + needed_items_levelup

        if category == 'environments':
            needed_items = needed_items_images + needed_items_locked

        needed_items = sorted(needed_items)

        if sorted(existing_items) != sorted(needed_items):
            print category, subcat
            for e in existing_items:
                if e not in needed_items:
                    print 'Leftover image: {}'.format(e)

            for n in needed_items:
                if n not in existing_items:
                    print 'Needed image: {}'.format(n)

            print
            ok = False

if ok:
    print 'All images are OK!'

