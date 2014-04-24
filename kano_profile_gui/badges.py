#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

#import os
#from gi.repository import Gtk

from kano.profile.badges import calculate_badges
from .images import get_image
#import kano_profile_gui.components.constants as constants
import kano_profile_gui.selection_table_components.table_template as table_template

img_width = 180
badge_ui = None


def activate(_win, _box):
    global badge_ui

    badges = {k: v for k, v in calculate_badges().iteritems() if not k.startswith('swag_')}
    if not badges:
        return

    #num_categories = len(badges.keys())
    #max_items = max([len(v) for k, v in badges.iteritems()])

    badges_info = []

    for i, (group, items) in enumerate(badges.iteritems()):
        for j, (item, unlocked) in enumerate(items.iteritems()):
            img_path = get_image("badges", item, group, img_width)
            badges_info.append({"filename": img_path, "heading": item, "description": group, "unlocked": unlocked})

    headers = ["badges"]
    # badge_info["badge1"] = {"filename": i, "heading": "heading", "description": "lots of info"}
    info = [badges_info]
    equipable = False
    width = 734
    height = 540

    if badge_ui is None:
        badge_ui = table_template.Template(headers, info, equipable, width, height)

    _box.pack_start(badge_ui.container, False, False, 0)

    _win.show_all()

    badge_ui.hide_labels()
