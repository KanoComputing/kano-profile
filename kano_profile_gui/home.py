#!/usr/bin/env python

# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk

from kano.profile.profile import load_profile
from kano.profile.badges import calculate_xp, calculate_kano_level


def activate(_win, _box, _label):
    _label.set_text('Home')

    profile = load_profile()

    xp = calculate_xp()
    level, progress = calculate_kano_level()
    name = profile['username_linux']

    msg = 'name: {}\nXP: {}\nLevel: {}\nProgress to next level: {:.0%}'.format(name, xp, level, progress)

    label = Gtk.Label()
    label.set_text(msg)
    _box.add(label)


