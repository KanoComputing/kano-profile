#!/usr/bin/env python

# environment_table.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size of the pictures displayed on the environment page

# Size: width = 230px, height = 180px


# Read from directory /usr/share/kano-profile/media/environments/*

from gi.repository import Gtk
import environment_pictures as pic


class Table():
    def __init__(self):

        self.width = 690
        self.height = 448

        self.environment_pictures = ["environment-1", "environment-2", "environment-3", "environment-4"]
        self.environment_info = ["environment-1 info", "environment-2 info", "environment-3 info", "environment-4 info"]

        self.number_of_columns = 3
        self.number_of_rows = 3

        self.buttons = []
        self.pics = []

        for x in range(len(self.environment_pictures)):
            picture = pic.Picture(self.environment_pictures[x], self.environment_info[x])
            self.pics.append(picture)

        # Attach to table
        index = 0
        row = 0

        # Create table from number of rows and columns - preferably dynamically
        self.table = Gtk.Table(3, 3)

        while index < len(self.environment_pictures):
            for j in range(self.number_of_columns):
                if index < len(self.environment_pictures):
                    self.table.attach(self.pics[index].button, j, j + 1, row, row + 1,
                                      Gtk.AttachOptions.EXPAND, Gtk.AttachOptions.EXPAND, 0, 0)
                    index += 1
            row += 1

        # Read config file/ JSON and find selected picture.  Default to first one
        self.selected = self.pics[0].fixed

    def set_selected(self, pic="None"):

        if pic is not None:
            self.selected = pic
            return

        for pic in self.pics:
            if pic.get_selected:
                self.selected = pic
                return

        self.selected = None

    def get_selected(self):
        return self.selected

