#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

#import os
#from gi.repository import Gtk

from kano.profile.badges import calculate_badges
import kano_profile_gui.selection_table_components.table_template as table_template

img_width = 180
badge_ui = None


def activate(_win, _box):
    global badge_ui

    badges = {k: v for k, v in calculate_badges().iteritems() if not k.startswith('swag_')}

    if not badges:
        return

    headers = ["badges"]
    info = [badges]
    equipable = False
    width = 734
    height = 540

    # So we don't overwrite the current selected items
    # If we read and write to a config file, this isn't needed
    if badge_ui is None:
        badge_ui = table_template.Template(headers, info, equipable, width, height)

    _box.pack_start(badge_ui.container, False, False, 0)

    _win.show_all()

    badge_ui.hide_labels()
