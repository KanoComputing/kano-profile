#!/usr/bin/env python

# Badges.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import math
from gi.repository import Gtk

import kano.profile as kp


def activate(_win, _box, _label):
    _label.set_text('Badges')

    badges = kp.calculate_badge()
    if not badges:
        return
    print badges

    total_number = len(badges)
    dim = int(math.ceil(math.sqrt(total_number)))

    if not dim:
        return

    table = Gtk.Table(dim, dim, True)
    _box.add(table)

    for i, badge in enumerate(badges):
        print i, badge, badges[badge]

