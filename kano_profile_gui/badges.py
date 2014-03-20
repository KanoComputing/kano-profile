#!/usr/bin/env python

# badges.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import math
from gi.repository import Gtk

import kano.profile as kp
import kano_profile_gui.images as images


def activate(_win, _box, _label):
    _label.set_text('Badges')

    badges = kp.calculate_badges_swags('badges')
    if not badges:
        return

    total_number = len(badges)
    dim = int(math.ceil(math.sqrt(total_number)))

    if not dim:
        return

    table = Gtk.Table(dim, dim, True)
    _box.add(table)

    for i, badge in enumerate(badges):
        x = i % dim
        y = i / dim

        images.check_image(badge, 'badge')

        btn = Gtk.Button(label=badge, halign=Gtk.Align.CENTER)
        btn.set_sensitive(badges[badge])
        table.attach(btn, x, x + 1, y, y + 1)
