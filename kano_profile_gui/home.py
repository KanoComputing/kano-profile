#!/usr/bin/env python

# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.profile.badges import calculate_xp, calculate_kano_level

import kano_profile_gui.home_components.home_stats as home_stats
import kano_profile_gui.home_components.home_picture as home_pic
from kano.world.functions import get_mixed_username


def activate(_win, _box):

    xp = calculate_xp()
    level, progress = calculate_kano_level()
    name = get_mixed_username()

    # Picture box - contains image depends on level reached
    picture_box = Gtk.Box()
    picture = home_pic.HomePicture().fixed
    picture_box.add(picture)

    # Stats
    stat_dict = {"Name": name, "XP": xp, "Level": level, "Progress": progress}
    stats = home_stats.HomeStats(_win.WINDOW_WIDTH, stat_dict)

    _box.pack_start(picture_box, False, False, 0)
    _box.pack_start(stats.container, False, False, 0)

    _win.progress.set_progress()

    _win.show_all()


