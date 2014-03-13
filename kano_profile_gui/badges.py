#!/usr/bin/env python

# badges.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk


def activate(_win, _table, _box):
    print __name__
    # Table
    table = Gtk.Table(4, 1, True)
    _box.add(table)

    # Label
    label = Gtk.Label()
    label.set_text("Badges")
    table.attach(label, 0, 1, 0, 1)

