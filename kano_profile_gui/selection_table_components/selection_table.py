#!/usr/bin/env python

# selection_table.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the table from which you can select backgrounds and avatars.


from gi.repository import Gtk
import kano_profile_gui.selection_table_components.individual_item as item
import kano_profile_gui.selection_table_components.equipable as equip


class Table():
    def __init__(self, info, equipable):
        self.width = 690
        self.height = 540
        self.equipable = equipable
        self.equipped = None

        #self.pictures = []
        #for item in info:
        #    self.pictures.append(item["name"])
        #self.info = info

        self.info = info
        self.number_of_columns = 3
        self.number_of_rows = (len(info) / self.number_of_columns) + (len(info) % self.number_of_columns)

        self.buttons = []
        self.pics = []

        for x in self.info:
            if self.equipable:
                picture = equip.Picture(x)
            else:
                picture = item.Picture(x)
            self.pics.append(picture)

        # Attach to table
        index = 0
        row = 0

        # Create table from number of rows and columns - preferably dynamically
        self.table = Gtk.Table(self.number_of_rows, self.number_of_columns)

        while index < (self.number_of_rows * self.number_of_columns):
            for j in range(self.number_of_columns):
                if index < len(self.info):
                    self.table.attach(self.pics[index].button, j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                else:
                    emptybox = Gtk.EventBox()
                    if index % 2 == 0:
                        emptybox.get_style_context().add_class("black")
                    else:
                        emptybox.get_style_context().add_class("white")
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
            if pic is not None:
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

