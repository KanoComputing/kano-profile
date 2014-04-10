#!/usr/bin/env python

# badges.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk

from kano.profile.badges import calculate_badges
from .images import get_image


def activate(_win, _box, _label):
    _label.set_text('Badges')

    badges = {k: v for k, v in calculate_badges().iteritems() if not k.startswith('swag_')}
    if not badges:
        return

    num_categories = len(badges.keys())
    max_items = max([len(v) for k, v in badges.iteritems()])

    table = Gtk.Table(max_items, num_categories, False)
    _box.add(table)

    for i, (group, items) in enumerate(badges.iteritems()):
        for j, item in enumerate(items):
            print i, j, group, item

            img = Gtk.Image()
            if badges[badge]:
                img_path = get_image(badge, 'badge', 100)
                img.set_from_file(img_path)
            else:
                img.set_from_file('/usr/share/kano-profile/media/icons/questionmark.png')

            table.attach(img, x, x + 1, y, y + 1)
