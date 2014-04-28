#!/usr/bin/env python

# selection_table.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the table from which you can select backgrounds and avatars.


from gi.repository import Gtk
import kano_profile_gui.selection_table_components.individual_item as indiv
import kano_profile_gui.selection_table_components.equipable as equip
from kano.profile.badges import calculate_badges
#from .images import get_image


class Table():
    def __init__(self, category_name, equipable):
        self.equipable = equipable
        self.equipped = None
        self.buttons = []
        self.pics = []

        number_of_badges = 0

        for category, items in calculate_badges(category_name).iteritems():
            for badge, properties in items.iteritems():
                #print category
                #print items
                #print badge
                #print properties
                if category == "swag_environments" or category == "swag_avatars":
                    category = ""
                cat_dict = {"category": category_name, "subcategory": category, "badge_name": badge, "title": properties["title"],
                            "locked_description": properties["desc_locked"], "unlocked_description": properties["desc_unlocked"],
                            "unlocked": properties['achieved'], "bg_color": properties["bg_color"]}  # "unlocked": properties['achieved']"
                if self.equipable:
                    picture = equip.Picture(cat_dict)
                else:
                    picture = indiv.Picture(cat_dict)
                self.pics.append(picture)
                number_of_badges = number_of_badges + 1

        #self.info = info
        self.number_of_columns = 3
        self.number_of_rows = (number_of_badges / self.number_of_columns) + (number_of_badges % self.number_of_columns)

        self.table = Gtk.Table(self.number_of_rows, self.number_of_columns)
        # set_size_request has no effect
        self.table.set_size_request(300, 448)

        # Attach to table
        index = 0
        row = 0

        while index < (self.number_of_rows * self.number_of_columns):
            for j in range(self.number_of_columns):
                if index < number_of_badges:
                    self.table.attach(self.pics[index].button, j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                else:
                    emptybox = Gtk.EventBox()
                    emptybox.set_size_request(230, 180)
                    self.table.attach(emptybox, j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                index += 1

            row += 1

        # Read config file/ JSON and find equipped picture.  Default to first one
        self.set_equipped(self.pics[0])

    def set_selected(self, item):
        for pic in self.pics:
            pic.set_selected(False)
        item.set_selected(True)

    def get_selected(self):
        for pic in self.pics:
            if pic.get_selected():
                return pic
        return None

    def set_equipped(self, pic=None):
        if self.equipable:
            if pic is not None and not pic.get_locked():
                self.equipped = pic
                pic.set_equipped(True)
                self.set_equipped_style()
                return

            for pic in self.pics:
                if pic.get_equipped():
                    self.equipped = pic
                    self.set_equipped_style()
                    return

            self.equipped = None
            self.set_equipped_style()

    def get_equipped(self):
        if self.equipable:
            return self.equipped

    def set_equipped_style(self):
        if self.equipable:
            for pic in self.pics:
                pic.remove_equipped_style()
                pic.set_equipped(False)

            if self.equipped is not None:
                self.equipped.add_equipped_style()
                self.equipped.set_equipped(True)

    def hide_labels(self):
        for pic in self.pics:
            pic.hover_box.set_visible_window(False)
            pic.hover_label.set_visible(False)
            if self.equipable and not pic.get_equipped():
                pic.equipped_box.set_visible_window(False)
                pic.equipped_label.set_visible(False)
            if not pic.get_locked():
                pic.remove_locked_style()

