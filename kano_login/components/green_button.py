#!/usr/bin/env python

# green_button.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Create a green button with white text inside

from gi.repository import Gtk
import kano_login.components.cursor as cursor


class Button():
    def __init__(self, text, win):
        self.button = Gtk.Button(text)
        self.button.get_style_context().add_class("green_button")

        self.box = Gtk.Box()
        self.box.add(self.button)
        self.button.props.halign = Gtk.Align.CENTER
        self.box.props.halign = Gtk.Align.CENTER

        self.align = Gtk.Alignment()
        self.align.add(self.box)

        self.hand_handler = self.button.connect('enter-notify-event',
                                                cursor.hand_cursor, win)
        self.arrow_handler = self.button.connect('leave-notify-event',
                                                 cursor.arrow_cursor, win)
        self.button.connect('button-press-event', cursor.arrow_cursor, win)

    def set_padding(self, top, bottom, left, right):
        self.align.set_padding(top, bottom, left, right)

    def disconnect_handlers(self):
        self.button.disconnect(self.hand_handler)
        self.button.disconnect(self.arrow_handler)
