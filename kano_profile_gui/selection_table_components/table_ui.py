#!/usr/bin/env python

# selection_table.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the table from which you can select backgrounds and avatars.


from gi.repository import Gtk
import kano_profile_gui.selection_table_components.item_ui as item_ui
import kano_profile_gui.selection_table_components.item_group as item_group
from kano_profile_gui.selection_table_components import item_info
from kano_profile.badges import calculate_badges
import math
#from .images import get_image


class TableUi():
    def __init__(self, category_name, equipable):
        self.equipable = equipable
        self.buttons = []
        self.pics = []
        self.group = None

        item_array = []
        number_of_badges = 0
        category_dict = calculate_badges()[category_name]

        # To access video dude jason:
        # calculate_badges()['avatars']['video_dude']
        # all_avatars = calculate_badges()['avatars']

        # cycle through all avatar_category, avatar_items like this:

        # for avatar_cat, avatar_items in all_avatars.iteritems():
        #   print avatar_cat, avatar_items

        for folder_name, items in category_dict.iteritems():
            for filename, properties in items.iteritems():
                cat_dict = {"category": category_name, "subcategory": folder_name, "badge_name": filename, "title": properties["title"],
                            "locked_description": properties["desc_locked"], "unlocked_description": properties["desc_unlocked"],
                            "unlocked": properties['achieved'], "bg_color": properties["bg_color"]}  # "unlocked": properties['achieved']

                item = item_info.ItemInfo(cat_dict)
                pic = item_ui.ItemUi(item)
                self.pics.append(pic)
                number_of_badges = number_of_badges + 1.0  # Make a float
                item_array.append(item)

        self.group = item_group.ItemGroup(item_array)

        self.number_of_columns = 3
        self.number_of_rows = math.ceil(number_of_badges / self.number_of_columns)

        self.grid = Gtk.Grid()

        # Attach to grid
        index = 0
        row = 0

        while index < (self.number_of_rows * self.number_of_columns):
            for j in range(self.number_of_columns):
                if index < number_of_badges:
                    self.grid.attach(self.pics[index].button, j, row, 1, 1)
                else:
                    emptybox = Gtk.EventBox()
                    emptybox.set_size_request(230, 180)
                    emptybox.get_style_context().add_class('emptybox')
                    self.grid.attach(emptybox, j, row, 1, 1)
                index += 1

            row += 1

        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)

    def hide_labels(self):
        for pic in self.pics:
            pic.hover_box.set_visible_window(False)
            pic.hover_label.set_visible(False)
            if self.equipable:
                pic.change_equipped_style()
            if not pic.get_locked():
                pic.change_locked_style()

    def unequip_all(self):
        self.group.unequip_all()
        for pic in self.pics:
            pic.set_equipped(False)

    def get_equipped_picture(self):
        for pic in self.pics:
            if pic.get_equipped():
                return pic
        return None

    def get_equipped_tuple(self):
        for pic in self.pics:
            if pic.get_equipped():
                return pic.item.get_tuple()
        return None

    def change_equipped_style(self):
        for pic in self.pics:
            pic.change_equipped_style()
