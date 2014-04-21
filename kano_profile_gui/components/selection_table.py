#!/usr/bin/env python

# selection_table.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size of the pictures displayed on the page

# Size: width = 230px, height = 180px


# Read from directory /usr/share/kano-profile/media/subfolder/*

from gi.repository import Gtk
import selection_picture as pic


class Table():
    def __init__(self, subfolder, pictures, info):
        self.width = 690
        self.height = 540

        self.pictures = pictures
        self.info = info

        self.number_of_columns = 3
        self.number_of_rows = 3

        self.buttons = []
        self.pics = []

        for x in range(len(self.pictures)):
            picture = pic.Picture(subfolder, self.pictures[x], self.info[x])
            self.pics.append(picture)

        # Attach to table
        index = 0
        row = 0

        # Create table from number of rows and columns - preferably dynamically
        self.table = Gtk.Table(self.number_of_rows, self.number_of_columns)

        while index < (self.number_of_rows * self.number_of_columns):
            for j in range(self.number_of_columns):
                if index < len(self.pictures):
                    self.table.attach(self.pics[index].button, j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                    self.pics[index].button.connect("button_press_event", self.select, self.pics[index])
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

        # Read config file/ JSON and find selected picture.  Default to first one
        self.set_selected(self.pics[0])

    def select(self, widget1=None, event=None, pic=None):
        self.set_selected(pic)

    def set_selected(self, pic="None"):

        if pic is not None:
            self.selected = pic
            pic.set_selected(True)
            self.set_selected_style()
            return

        for pic in self.pics:
            if pic.get_selected():
                self.selected = pic
                self.set_selected_style()
                return

        self.selected = None
        self.set_selected_style()

    def get_selected(self):
        return self.selected

    def set_selected_style(self):
        for pic in self.pics:
            pic.remove_selected_style()
            pic.set_selected(False)

        if self.selected is not None:
            self.selected.add_selected_style()
            self.selected.set_selected(True)

    def unselect_all(self):
        for pic in self.pics:
            if not pic.get_selected():
                pic.hover_label.set_visible_window(False)
                pic.hover_text.set_visible(False)
                pic.selected_label.set_visible_window(False)
                pic.selected_text.set_visible(False)

