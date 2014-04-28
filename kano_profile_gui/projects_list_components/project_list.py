#!/usr/bin/env python

# project_list.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Scrolled window containing all challenges

from gi.repository import Gtk
import kano_profile_gui.projects_list_components.project_item as item
import kano_profile_gui.components.constants as constants


# info is a dictionary/ array of info
class List():
    def __init__(self, info=None):
        self.background = Gtk.EventBox()
        self.background.get_style_context().add_class("project_list_background")

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        for n in range(10):
            title = "title" + str(n)
            time = "time" + str(n)
            filename = constants.media + "/images/icons/Level-1.png"

            self.item = item.Item(title, time, filename)
            self.container.pack_start(self.item.background, False, False, 0)

        self.align = Gtk.Alignment(xalign=0.5, yalign=0.5)
        self.align.set_padding(10, 10, 20, 20)
        self.align.add(self.container)
        self.background.add(self.align)

