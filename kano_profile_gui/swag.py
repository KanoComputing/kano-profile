#!/usr/bin/env python

# swag.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk


def activate(_win, _box, _label):
    _label.set_text('Swag')

    msg = 'Swag'

    label = Gtk.Label()
    label.set_text(msg)
    _box.add(label)
