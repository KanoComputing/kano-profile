#!/usr/bin/env python

# selection_table.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the table from which you can select backgrounds and avatars.


from gi.repository import Gtk
import kano_profile_gui.selection_table_components.item_ui as item_ui
from kano_profile_gui.selection_table_components import item_info, item_group
from kano.profile.badges import calculate_badges
#from .images import get_image


class TableUi():
    def __init__(self, category_name, equipable):
        self.equipable = equipable
        self.buttons = []
        self.pics = []
        self.item_groups = []

        number_of_badges = 0
        category_dict = calculate_badges()[category_name]

        # To access video dude jason:
        # calculate_badges()['avatars']['video_dude']
        # all_avatars = calculate_badges()['avatars']

        # cycle through all avatar_category, avatar_items like this:

        # for avatar_cat, avatar_items in all_avatars.iteritems():
        #   print avatar_cat, avatar_items

        for folder_name, items in category_dict.iteritems():
            item_array = []
            for filename, properties in items.iteritems():
                cat_dict = {"category": category_name, "subcategory": folder_name, "badge_name": filename, "title": properties["title"],
                            "locked_description": properties["desc_locked"], "unlocked_description": properties["desc_unlocked"],
                            "unlocked": True, "bg_color": properties["bg_color"]}  # "unlocked": properties['achieved']

                item = item_info.ItemInfo(cat_dict)

                if category_name != "avatars":
                    group = item_group.ItemGroup([item])
                    pic = item_ui.ItemUi(group)
                    self.pics.append(pic)
                    number_of_badges = number_of_badges + 1
                else:
                    item_array.append(item)

            if category_name == "avatars":
                group = item_group.ItemGroup(item_array)
                self.item_groups.append(group)
                pic = item_ui.ItemUi(group)
                self.pics.append(pic)

                number_of_badges = number_of_badges + 1

        #self.info = info
        self.number_of_columns = 3
        self.number_of_rows = (number_of_badges / self.number_of_columns) + (number_of_badges % self.number_of_columns)

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
                    self.grid.attach(emptybox, j, row, 1, 1)
                index += 1

            row += 1

        # Read config file/ JSON and find equipped picture.  Default to first one
        #self.set_equipped(self.pics[0])
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)

    def hide_labels(self):
        for pic in self.pics:
            pic.hover_box.set_visible_window(False)
            pic.hover_label.set_visible(False)
            if self.equipable and pic.get_equipped_item() is None:
                pic.change_equipped_style()
            if not pic.get_locked():
                pic.change_locked_style()

    def unequip_all(self):
        for i in self.pics:
            i.unequip_all()

    def get_equipped_picture(self):
        for pic in self.pics:
            if pic.get_equipped_item() is not None:
                return pic
        return None

    def get_equipped_tuple(self):
        for pic in self.pics:
            if pic.get_equipped_item() is not None:
                return pic.get_equipped_item().get_tuple()
        return None
