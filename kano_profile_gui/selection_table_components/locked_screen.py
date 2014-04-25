#!/usr/bin/env python

# locked_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
import kano_profile_gui.components.constants as constants


class Screen():
    def __init__(self, width, height, left_margin, top_margin):
        self.box = Gtk.EventBox()
        self.box.get_style_context().add_class("locked_box")
        self.box.set_size_request(width, height)
        self.padlock = Gtk.Image()
        self.padlock.set_from_file(constants.media + "/images/icons/Level-4.png")
        self.fixed = Gtk.Fixed()
        self.fixed.put(self.box, 0, 0)
        self.fixed.put(self.padlock, left_margin, top_margin)
