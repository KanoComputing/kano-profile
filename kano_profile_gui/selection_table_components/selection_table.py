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
#from kano.profile.badges import calculate_badges
#from .images import get_image


class Table():
    def __init__(self, category_dict, equipable):
        self.width = 690
        self.height = 540
        self.equipable = equipable
        self.equipped = None
        self.buttons = []
        self.pics = []

        number_of_badges = 0

        for i, (group, items) in enumerate(category_dict.iteritems()):
            for j, (item, unlocked) in enumerate(items.iteritems()):
                if self.equipable:
                    # Passing the item and group instead of the filename because the filename depends on the size, and the size varies
                    # depending on what you need the image for.
                    # TODO: change colour of badge background
                    picture = equip.Picture({"item": item, "group": group, "heading": item, "description": group, "unlocked": unlocked, "color": "#ff0000"})
                    self.pics.append(picture)
                else:
                    #picture = indiv.Picture({"filename": img_path, "heading": item, "description": group, "unlocked": unlocked,})
                    picture = indiv.Picture({"item": item, "group": group, "heading": item, "description": group, "unlocked": unlocked, "color": "#ff0000"})
                    self.pics.append(picture)
                number_of_badges = number_of_badges + 1

        #self.info = info
        self.number_of_columns = 3
        self.number_of_rows = (number_of_badges / self.number_of_columns) + (number_of_badges % self.number_of_columns)

        self.table = Gtk.Table(self.number_of_rows, self.number_of_columns)

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

