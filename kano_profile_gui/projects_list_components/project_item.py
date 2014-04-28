#!/usr/bin/env python

# project_item.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# controls UI of individual item in project UI

from gi.repository import Gtk


class Item():
    def __init__(self, title, time, filename):
        self.background = Gtk.EventBox()
        self.background.get_style_context().add_class("white")

        self.button = Gtk.Button("MAKE")
        self.button.connect("button-press-event", self.make)
        self.button.get_style_context().add_class("project_make_button")
        self.button_padding = Gtk.Alignment()
        self.button_padding.set_padding(10, 10, 10, 10)
        self.button_padding.add(self.button)

        self.title = Gtk.Label(title)
        self.title.get_style_context().add_class("project_item_title")
        self.title.set_alignment(xalign=0, yalign=1)
        self.title.set_padding(10, 0)
        self.time = Gtk.Label(time)
        self.time.get_style_context().add_class("project_item_time")
        self.time.set_alignment(xalign=0, yalign=0.5)
        self.time.set_padding(10, 0)

        self.label_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.label_container.pack_start(self.title, False, False, 0)
        self.label_container.pack_start(self.time, False, False, 0)
        #self.label_container.set_size_request(450, 0)

        self.label_align = Gtk.Alignment(xalign=0, yalign=0.5)
        self.label_align.add(self.label_container)
        self.label_align.set_padding(10, 10, 10, 0)

        self.image = Gtk.Image()
        self.image.set_from_file(filename)

        self.container = Gtk.Box()
        self.container.pack_start(self.image, False, False, 0)
        self.container.pack_start(self.label_align, False, False, 0)
        self.container.pack_end(self.button_padding, False, False, 0)

        self.background.add(self.container)

    def make(self, arg1=None, arg2=None):
        print "Making project!"


