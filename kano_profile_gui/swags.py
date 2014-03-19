#!/usr/bin/env python

# swags.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import math
from gi.repository import Gtk

import kano.profile as kp


def activate(_win, _box, _label):
    _label.set_text('swags')

    swags = kp.calculate_swags()
    if not swags:
        return
    print swags

    total_number = len(swags)
    dim = int(math.ceil(math.sqrt(total_number)))

    if not dim:
        return

    table = Gtk.Table(dim, dim, True)
    _box.add(table)

    for i, swag in enumerate(swags):
        x = i % dim
        y = i / dim

        btn = Gtk.Button(label=swag, halign=Gtk.Align.CENTER)
        btn.set_sensitive(swags[swag])
        table.attach(btn, x, x + 1, y, y + 1)
