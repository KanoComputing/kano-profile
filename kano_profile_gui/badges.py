#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

#import os
from gi.repository import Gtk

import os
#from kano.profile.badges import calculate_badges
#from .images import get_image
#from .paths import icon_dir
import kano_profile_gui.components.header as header
import kano_profile_gui.selection_table_components.selection_table as tab
import kano_profile_gui.selection_table_components.info_screen as info_screen
import kano_profile_gui.components.constants as constants

img_width = 50
badge_ui = None


class Ui():
    def __init__(self):

        filenames = []

        #for file in os.listdir(constants.media + "/badges/"):
        #    if file.endswith(".png"):
        #        print file

        for root, dirs, files in os.walk(constants.media + "/badges/"):
            for file in files:
                if file.endswith(".png"):
                    filenames.append(os.path.join(root, file))

        badges_info = []

        for i in filenames:
            line = {"filename": i, "heading": "heading", "description": "lots of info"}
            badges_info.append(line)

        self.head = header.Header("Badges")
        self.badges = tab.Table(badges_info, False)

        for pic in self.badges.pics:
            pic.button.connect("button_press_event", self.selected_item_screen, self.badges.pics, pic)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.add_with_viewport(self.badges.table)
        self.scrolledwindow.set_size_request(self.badges.width + 44, self.badges.height)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.container.pack_start(self.head.box, False, False, 0)
        self.container.pack_start(self.scrolledwindow, False, False, 0)

    def selected_item_screen(self, arg1=None, arg2=None, array=[], selected_item=None):
        selected_item_screen = info_screen.Item(array, selected_item, False)
        for i in self.container.get_children():
            self.container.remove(i)
        self.container.add(selected_item_screen.container)
        selected_item_screen.info.back_button.connect("button_press_event", self.leave_info_screen)
        self.container.show_all()

    def leave_info_screen(self, arg1=None, arg2=None):
        for i in self.container.get_children():
            self.container.remove(i)
        self.container.pack_start(self.head.box, False, False, 0)
        self.container.pack_start(self.scrolledwindow, False, False, 0)
        self.container.show_all()
        # Hide all labels on images
        self.badges.hide_labels()


def activate(_win, _box):
    global badge_ui

    """_label.set_text('Badges')

                badges = {k: v for k, v in calculate_badges().iteritems() if not k.startswith('swag_')}
                if not badges:
                    return

                num_categories = len(badges.keys())
                max_items = max([len(v) for k, v in badges.iteritems()])

                table = Gtk.Table(num_categories, max_items, False)
                _box.add(table)

                for i, (group, items) in enumerate(badges.iteritems()):
                    for j, (item, unlocked) in enumerate(items.iteritems()):
                        print i, j, group, item, unlocked

                        img = Gtk.Image()
                        if unlocked:
                            img_path = get_image(item, group, img_width)
                            img.set_from_file(img_path)
                        else:
                            img.set_from_file(os.path.join(icon_dir, str(img_width), '_locked.png'))

                        table.attach(img, j, j + 1, i, i + 1)"""

    if badge_ui is None:
        badge_ui = Ui()

    _box.pack_start(badge_ui.container, False, False, 0)

    _win.show_all()

    badge_ui.badges.hide_labels()
