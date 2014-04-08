#!/usr/bin/env python

# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano.profile as kp
import kano_profile_gui.components.home_stats as home_stats

PICTURE_HEIGHT = 250


def activate(_win, _box, _label):
    _label.set_text('Home')

    profile = kp.load_profile()

    xp = kp.calculate_xp()
    level, progress = kp.calculate_kano_level()
    name = profile['username_linux']

    # Picture box - contains image depends on level reached
    picture_box = Gtk.Box()
    # 300 is currently a "magic number", to fill up window size
    picture_box.set_size_request(_win.WINDOW_WIDTH, PICTURE_HEIGHT)

    picture = Gtk.Image()
    picture.set_from_file("/home/caroline/kano-profile/media/screens/home.png")

    picture_box.add(picture)

    # Stats
    stat_dict = {"Name": name, "XP": xp, "Level": level, "Progress": progress}
    stats = home_stats.Stats(_win.WINDOW_WIDTH, stat_dict)

    _box.pack_start(picture_box, False, False, 0)
    _box.pack_start(stats.container, False, False, 0)

    #msg = 'name: {}\nXP: {}\nLevel: {}\nProgress to next level: {:.0%}'.format(name, xp, level, progress)

    #label = Gtk.Label()
    #label.set_text(msg)
    #_box.add(label)


