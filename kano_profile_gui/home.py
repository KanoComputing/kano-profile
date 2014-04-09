#!/usr/bin/env python

# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano.profile as kp


def activate(_win, _box, _label):
    _label.set_text('Home')

    profile = kp.load_profile()

    xp = kp.calculate_xp()
    level, progress = kp.calculate_kano_level()
    name = profile['username_linux']

    msg = 'name: {}\nXP: {}\nLevel: {}\nProgress to next level: {:.0%}'.format(name, xp, level, progress)

    label = Gtk.Label()
    label.set_text(msg)
    _box.add(label)


