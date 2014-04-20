#!/usr/bin/env python

# home_picture.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size of the pictures displayed on the environment page

# Size: width = 230px, height = 180px

# Read from directory /usr/share/kano-profile/media/environments/*

from gi.repository import Gtk, GdkPixbuf


class Picture():
    def __init__(self):

        self.width = 690
        self.height = 448

        #for picture in self.environment_picture:
        filename = "/usr/share/kano-profile/media/environments/environment-1.png"
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, self.width, self.height)
        self.image = Gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
