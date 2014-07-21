#!/usr/bin/env python

# top_bar_template.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Template for a window with a top bar

from gi.repository import Gtk
from kano.gtk3.top_bar import TopBar


class TopBarTemplate(Gtk.Grid):
    def __init__(self, title_name=""):
        Gtk.Grid.__init__(self)
        self.top_bar = TopBar(title=title_name, window_width=590, has_buttons=False)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.attach(self.top_bar, 0, 0, 3, 1)
        self.attach(self.box, 1, 1, 1, 1)

        #self.top_bar.set_prev_callback(prev_cb, args)
        #self.top_bar.set_next_callback(next_callback)
        self.top_bar.set_close_callback(Gtk.main_quit)

    def enable_prev(self):
        self.top_bar.enable_prev()

    def enable_next(self):
        self.top_bar.enable_next()

    def disable_prev(self):
        self.top_bar.disable_prev()

    def disable_next(self):
        self.top_bar.disable_next()
