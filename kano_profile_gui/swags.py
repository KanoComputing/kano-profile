#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

#import os
from gi.repository import Gtk

from kano.profile.badges import calculate_badges
from .images import get_image
from .paths import icon_dir

import kano_profile_gui.components.selection_table as tab
import kano_profile_gui.components.header as header

img_width = 50
swag_ui = None


class Ui():
    def __init__(self):

        environ_pictures = ["environment-1", "environment-2", "environment-3", "environment-4", "environment-5", "environment-6"]
        environ_info = ["environment-1 info", "environment-2 info", "environment-3 info", "environment-4 info", "environment-5 info", "environment-6 info"]

        avatar_pictures = ["avatar-1", "avatar-2"]
        avatar_info = ["avatar-1 info", "avatar-2 info"]

        self.head = header.Header("Environments", "Avatars")
        self.head.radiobutton1.connect("toggled", self.on_button_toggled)

        self.environments = tab.Table("environments", environ_pictures, environ_info)
        self.avatars = tab.Table("avatars", avatar_pictures, avatar_info)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.add(self.environments.table)
        self.scrolledwindow.set_size_request(self.environments.width, self.environments.height)

    def on_button_toggled(self, radio):
        in_environments = radio.get_active()

        container = self.environments.table.get_parent()
        if container is not None:
            container.remove(self.environments.table)

        container = self.avatars.table.get_parent()
        if container is not None:
            container.remove(self.avatars.table)

        for i in self.scrolledwindow.get_children():
                self.scrolledwindow.remove(i)

        if in_environments:
            self.scrolledwindow.add(self.environments.table)
        else:
            self.scrolledwindow.add(self.avatars.table)

        self.scrolledwindow.show_all()
        self.environments.unselect_all()
        self.avatars.unselect_all()


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

    if swag_ui is None:
        swag_ui = Ui()

    _box.pack_start(swag_ui.head.box, False, False, 0)
    _box.pack_start(swag_ui.scrolledwindow, False, False, 0)

    _win.show_all()

    # Hide all labels on images
    swag_ui.environments.unselect_all()
    swag_ui.avatars.unselect_all()
