#!/usr/bin/env python

# heading.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is the container and text (title and description) of each of the projects

from gi.repository import Gtk


class Heading():
    def __init__(self, title, description):

        self.title = Gtk.Label(title)
        self.description = Gtk.Label(description)

        self.title_style = self.title.get_style_context()
        self.title_style.add_class('title')

        self.description_style = self.description.get_style_context()
        self.description_style.add_class('description')

        # Table
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.container.pack_start(self.title, False, False, 6)
        self.container.pack_start(self.description, False, False, 0)

    def set_text(self, title, description):
        self.title.set_text(title)
        self.description.set_text(description)

    def get_text(self):
        return [self.title.get_text(), self.description.get_text()]
