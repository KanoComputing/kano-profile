#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk

from kano.profile.badges import calculate_badges
from .images import get_image
from .paths import icon_dir

img_width = 50


def activate(_win, _box, _label):
    _label.set_text('Badges')

    badges = {k: v for k, v in calculate_badges().iteritems() if not k.startswith('swag_')}
    if not badges:
        return

    num_categories = len(badges.keys())
    max_items = max([len(v) for k, v in badges.iteritems()])

    table = Gtk.Table(num_categories, max_items, False)
    _box.add(table)

    for i, (group, items) in enumerate(badges.iteritems()):
        for j, (item, unlocked) in enumerate(items.iteritems()):
            print i, j, group, item, unlocked

            img = Gtk.Image()
            if unlocked:
                img_path = get_image(item, group, img_width)
                img.set_from_file(img_path)
            else:
                img.set_from_file(os.path.join(icon_dir, str(img_width), '_locked.png'))

            table.attach(img, j, j + 1, i, i + 1)
