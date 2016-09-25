#!/usr/bin/env python

# ValidationEntry.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#


import os
import sys

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)
        print sys.path

from gi.repository import Gtk, GdkPixbuf
from kano_profile_gui.paths import media_dir


class ValidationEntry(Gtk.Entry):

    def __init__(self):
        Gtk.Entry.__init__(self)

    def set_image(self, name=""):
        if name == 'success':
            filename = os.path.join(media_dir, "images/icons/success.png")
        elif name == 'fail':
            filename = os.path.join(media_dir, "images/icons/error.png")
        else:
            # if name not correct, leave it blank
            filename = None

        if filename:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 30, 30)
        else:
            # If pixbuf is None, then the entry should be blank
            pixbuf = None

        self.set_icon_from_pixbuf(Gtk.EntryIconPosition.SECONDARY, pixbuf)
