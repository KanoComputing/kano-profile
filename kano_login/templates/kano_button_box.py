#!/usr/bin/env python

# kano_button_box.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Button box template
#

from gi.repository import Gtk
from kano.gtk3.buttons import KanoButton, OrangeButton


class KanoButtonBox(Gtk.Box):

    def __init__(self, kano_button_text, orange_text="", orange_text_2="", orange_text_3=""):

        Gtk.Box.__init__(self)
        self.kano_button = KanoButton(kano_button_text)

        if orange_text != "":
            self.orange_button = OrangeButton(orange_text)
            self.pack_start(self.orange_button, False, False, 0)
            self.pack_start(self.kano_button, False, False, 0)

            if orange_text_2 == "":
                # The empty label is to centre the kano_button
                label = Gtk.Label("    ")
                self.pack_start(label, False, False, 0)
            else:
                self.orange_button2 = OrangeButton(orange_text_2)
                if orange_text_3 == "":
                    self.pack_start(self.orange_button2, False, False, 0)
                else:
                    # If two orange button texts, we align them vertically
                    self.vertbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                    self.add(self.vertbox)
                    self.orange_button3 = OrangeButton(orange_text_3)
                    self.vertbox.pack_start(self.orange_button2, False, False, 0)
                    self.vertbox.pack_start(self.orange_button3, False, False, 0)
        else:
            self.pack_start(self.kano_button, False, False, 0)

    def get_kano_button(self):
        return self.kano_button

    def set_kano_button_cb(self, cb, args=[]):
        self.kano_button.connect('button-release-event', cb, args)

    def set_orange_button_cb(self, cb, args=[]):
        self.orange_button.connect('button-release-event', cb, args)

    def set_orange_button2_cb(self, cb, args=None):
        self.orange_button2.connect('button-release-event', cb, args)

    def set_orange_button3_cb(self, cb, args=None):
        self.orange_button3.connect('button-release-event', cb, args)
