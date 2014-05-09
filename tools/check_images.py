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

ok = True
for category, subcats in all_rules.iteritems():
    for subcat, items in subcats.iteritems():
        path = os.path.join(image_dir, category, 'originals', subcat)

        existing_items = sorted([f for f in os.listdir(path)])
        needed_items_images = ['{}.png'.format(f) for f in items.keys()]
        needed_items_locked = ['{}_locked.png'.format(f) for f in items.keys()]
        needed_items_circular = ['{}_circular.png'.format(f) for f in items.keys()]

        if category == 'avatars':
            needed_items = needed_items_images + needed_items_locked + needed_items_circular
        else:
            needed_items = needed_items_images + needed_items_locked

        needed_items = sorted(needed_items)

        if sorted(existing_items) != sorted(needed_items):
            print category, subcat
            print 'Existing images:\n{}'.format(', '.join(existing_items))
            print 'Needed images:\n{}'.format(', '.join(needed_items))
            print
            ok = False

if ok:
    print 'All images are OK!'

