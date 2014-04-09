#!/usr/bin/env python

# green_button.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Create a green button with white text inside

from gi.repository import Gtk


class Button():
    def __init__(self, text):
        self.label = Gtk.Label(text)
        self.label.get_style_context().add_class("white_label")
        self.button = Gtk.EventBox()
        self.button.set_size_request(100, 44)
        self.button.add(self.label)
        self.button.get_style_context().add_class("green_event_box")

        self.box = Gtk.Box()
        self.box.add(self.button)
        self.button.props.halign = Gtk.Align.CENTER
        self.box.props.halign = Gtk.Align.CENTER

        #valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        #padding_above = 20
        #valign.set_padding(padding_above, 0, 0, 0)
        #valign.add(container)
