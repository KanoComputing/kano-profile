#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

#import os
from gi.repository import Gtk

from kano.profile.badges import calculate_badges
#from .images import get_image
#from .paths import icon_dir

import kano_profile_gui.components.selection_table as tab
import kano_profile_gui.components.header as header
import kano_profile_gui.components.info_screen as selected

img_width = 50
swag_ui = None


class Ui():
    def __init__(self):

        environ_info = [{"name": "environment-1", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"},
                        {"name": "environment-2", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"},
                        {"name": "environment-3", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"},
                        {"name": "environment-4", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"},
                        {"name": "environment-5", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"},
                        {"name": "environment-6", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"}]

        avatar_info = [{"name": "avatar-1", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"},
                       {"name": "avatar-2", "heading": "heading", "date": "date changed", "description": "lots of info", "hover_over_info": "hover over info"}]

        self.head = header.Header("Environments", "Avatars")
        self.head.radiobutton1.connect("toggled", self.on_button_toggled)

        self.environments = tab.Table("environments", environ_info)
        self.avatars = tab.Table("avatars", avatar_info)

        for pic in self.environments.pics:
            pic.button.connect("button_press_event", self.selected_item_screen, self.environments.pics, pic)

        for pic in self.avatars.pics:
            pic.button.connect("button_press_event", self.selected_item_screen, self.avatars.pics, pic)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.add(self.environments.table)
        self.scrolledwindow.set_size_request(self.environments.width, self.environments.height)

        self.container = Gtk.Box()
        self.container.add(self.scrolledwindow)

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
        self.environments.hide_labels()
        self.avatars.hide_labels()

    def selected_item_screen(self, arg1=None, arg2=None, array=[], selected_item=None):
        selected_item_screen = selected.Item(array, selected_item)
        for i in self.container.get_children():
            self.container.remove(i)
        self.container.add(selected_item_screen.box)
        selected_item_screen.info.back_button.connect("button_press_event", self.leave_info_screen)
        self.container.show_all()

    def leave_info_screen(self, arg1=None, arg2=None):
        for i in self.container.get_children():
            self.container.remove(i)
        self.container.add(self.scrolledwindow)
        self.container.show_all()
        # Hide all labels on images
        self.environments.hide_labels()
        self.avatars.hide_labels()


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
    _box.pack_start(swag_ui.container, False, False, 0)

    _win.show_all()

    # Hide all labels on images
    swag_ui.environments.hide_labels()
    swag_ui.avatars.hide_labels()
