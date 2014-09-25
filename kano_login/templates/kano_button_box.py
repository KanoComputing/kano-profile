
#!/usr/bin/env python

# kano_button_box.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Button box template
#

from gi.repository import Gtk
from kano.gtk3.buttons import KanoButton, OrangeButton


class KanoButtonBox(Gtk.ButtonBox):

    def __init__(self, kano_button_text, orange_text="", orange_text_2=""):

        Gtk.ButtonBox.__init__(self)
        self.set_layout(Gtk.ButtonBoxStyle.EDGE)

        self.kano_button = KanoButton(kano_button_text)

        if not orange_text == "":
            self.orange_button = OrangeButton(orange_text)
            self.pack_start(self.orange_button, False, False, 0)
            self.pack_start(self.kano_button, False, False, 0)

            if orange_text_2 == "":
                # The empty label is to centre the kano_button
                label = Gtk.Label("    ")
                self.pack_start(label, False, False, 0)
            else:
                self.orange_button2 = OrangeButton(orange_text_2)
                self.pack_start(self.orange_button2, False, False, 0)
        else:
            self.pack_start(self.kano_button, False, False, 0)

    def get_kano_button(self):
        return self.kano_button

    def set_kano_button_cb(self, cb, args=[]):
        self.kano_button.connect("button-release-event", cb, args)

    def set_orange_button_cb(self, cb, args=[]):
        self.orange_button.connect("button-release-event", cb, args)

    def set_orange_button2_cb(self, cb, args=None):
        self.orange_button2.connect("button-release-event", cb, args)
