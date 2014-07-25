#!/usr/bin/env python

# top_bar_template.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Template for a window with a top bar

from gi.repository import Gtk
from kano.gtk3.top_bar import TopBar
from kano.gtk3.kano_dialog import KanoDialog
from kano_login.data import get_data


class TopBarTemplate(Gtk.Grid):
    def __init__(self, title_name="", prev_screen=None):
        Gtk.Grid.__init__(self)
        self.top_bar = TopBar(title=title_name, window_width=590, has_buttons=True)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.prev_screen = prev_screen

        self.attach(self.top_bar, 0, 0, 3, 1)
        self.attach(self.box, 1, 1, 1, 1)

        if prev_screen:
            self.top_bar.set_prev_callback(self.show_prev_screen)

        self.top_bar.set_close_callback(self.close_window)

    def enable_prev(self):
        self.top_bar.enable_prev()

    def enable_next(self):
        self.top_bar.enable_next()

    def disable_prev(self):
        self.top_bar.disable_prev()

    def disable_next(self):
        self.top_bar.disable_next()

    def close_window(self, widget, event):
        # check for first boot
        data = get_data("CLOSE_WINDOW")
        kd = KanoDialog(
            data["LABEL_1"],
            data["LABEL_2"],
            {
                "OK": {"return_value": 0},
                "CANCEL": {"return_value": 1}
            },
            parent_window=widget.get_window()
        )

        response = kd.run()
        if response == 0:
            Gtk.main_quit()

    def show_prev_screen(self, widget, event):
        self.prev_screen.repack()
