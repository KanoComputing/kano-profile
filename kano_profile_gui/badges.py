#!/usr/bin/env python

# badges.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import math
from gi.repository import Gtk

from kano.profile.badges import calculate_badges
from .images import get_image


def activate(_win, _box, _label):
    _label.set_text('Badges')

    badges = calculate_badges()
    if not badges:
        return

    total_number = len(badges)
    dim = int(math.ceil(math.sqrt(total_number)))

    table = Gtk.Table(dim, dim, False)
    _box.add(table)

    for i, badge in enumerate(badges):
        x = i % dim
        y = i / dim

        img = Gtk.Image()
        if badges[badge]:
            img_path = get_image(badge, 'badge')
            img.set_from_file(img_path)
        else:
            img.set_from_file('/usr/share/kano-profile/media/icons/questionmark.png')

        table.attach(img, x, x + 1, y, y + 1)
