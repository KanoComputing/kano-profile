#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# swags.py
#
# Controls UI of swag screen

#from gi.repository import Gtk

import os

from kano.profile.badges import calculate_badges
#from .images import get_image
#from .paths import icon_dir

#import kano_profile_gui.selection_table_components.selection_table as tab
#import kano_profile_gui.selection_table_components.info_screen as info_screen
#import kano_profile_gui.components.header as header
import kano_profile_gui.components.constants as constants
import kano_profile_gui.selection_table_components.table_template as table_template

img_width = 50
swag_ui = None


def activate(_win, _box):
    global swag_ui
    #_label.set_text('Swags')

    badges = {k: v for k, v in calculate_badges().iteritems() if k.startswith('swag_')}
    if not badges:
        return

    ## Zsolt's code

    """ num_categories = len(badges.keys())
    max_items = max([len(v) for k, v in badges.iteritems()])

    table = Gtk.Table(num_categories, max_items, False)
    _box.add(table)

    for i, (group, items) in enumerate(badges.iteritems()):
        for j, item in enumerate(items):
            print i, j, group, item, items[item]

            img = Gtk.Image()
            if items[item]:
                img_path = get_image(item, group, img_width)
                img.set_from_file(img_path)
            else:
                img.set_from_file(os.path.join(icon_dir, str(img_width), '_locked.png'))

            table.attach(img, j, j + 1, i, i + 1)"""

    ##### My code ####

    environ_filenames = []

    for root, dirs, files in os.walk(constants.media + "/environments/"):
        for file in files:
            if file.endswith(".png"):
                #print os.path.join(root, file)
                environ_filenames.append(os.path.join(root, file))

    environ_info = []

    for i in environ_filenames:
        line = {"filename": i, "heading": "heading", "description": "lots of info", "color": "#ff0000"}
        environ_info.append(line)

    avatar_filenames = []

    for root, dirs, files in os.walk(constants.media + "/avatars/"):
        for file in files:
            if file.endswith(".png"):
                #print os.path.join(root, file)
                avatar_filenames.append(os.path.join(root, file))

    avatar_info = []

    for i in avatar_filenames:
        line = {"filename": i, "heading": "heading", "description": "lots of info", "color": "#00ff00"}
        avatar_info.append(line)

    headers = ["environments", "avatars"]
    info = [environ_info, avatar_info]
    equipable = True
    width = 734
    height = 540

    if swag_ui is None:
        swag_ui = table_template.Template(headers, info, equipable, width, height)

    _box.pack_start(swag_ui.container, False, False, 0)

    _win.show_all()

    # Hide all labels on images
    swag_ui.hide_labels()
