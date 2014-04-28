#!/usr/bin/env python

# header.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This is the header containing the number of locked and unlocked items info

from gi.repository import Gtk
import kano_profile_gui.components.icons as icons


class Header():
    def __init__(self, title1, title2=None):
        # Width of window plus scrollbar
        self.width = 690 + 44
        self.height = 44
        self.locked_elements = 5  # For now
        self.unlocked_elements = 5  # For now

        self.box = Gtk.Box()
        self.box.set_size_request(self.width, self.height)

        locked_pic = icons.set_from_name("locked")
        self.locked_label = Gtk.Label(": " + str(self.locked_elements))
        self.locked_label.get_style_context().add_class("padlock_label")
        locked_box = Gtk.Box()
        locked_box.pack_start(locked_pic, False, False, 0)
        locked_box.pack_start(self.locked_label, False, False, 0)

        unlocked_pic = icons.set_from_name("unlocked")
        self.unlocked_label = Gtk.Label(": " + str(self.unlocked_elements))
        self.unlocked_label.get_style_context().add_class("padlock_label")
        unlocked_box = Gtk.Box()
        unlocked_box.pack_start(unlocked_pic, False, False, 0)
        unlocked_box.pack_start(self.unlocked_label, False, False, 0)

        self.halign = Gtk.Alignment(xalign=0, yalign=0)

        self.title_label1 = Gtk.Label(title1.upper())
        self.title_label1.get_style_context().add_class("heading")

        self.title_label2 = None

        # If there are two titles, then we need to have 2 radio button to switch views
        if title2 is not None:
            self.title_label2 = Gtk.Label(title2.upper())
            self.title_label2.get_style_context().add_class("heading")
            self.radiobutton1 = Gtk.RadioButton()
            self.radiobutton2 = Gtk.RadioButton.new_from_widget(self.radiobutton1)
            self.container = Gtk.Box()
            self.container.pack_start(self.title_label1, False, False, 10)
            self.container.pack_start(self.radiobutton1, False, False, 0)
            self.container.pack_start(self.radiobutton2, False, False, 0)
            self.container.pack_start(self.title_label2, False, False, 10)
            self.halign.add(self.container)

        else:
            self.halign.add(self.title_label1)

        # 610 - magic number. :(
        self.halign.set_size_request(610, self.height)
        top_padding = 5
        bottom_padding = 0
        left_padding = 140
        right_padding = 140
        self.halign.set_padding(top_padding, bottom_padding, left_padding, right_padding)

        self.box.pack_start(locked_box, False, False, 5)
        self.box.pack_start(self.halign, False, False, 0)
        self.box.pack_start(unlocked_box, False, False, 0)

    def set_locked(self, number_of_locked):
        self.locked_elements = number_of_locked
        self.locked_label.show()

    def set_unlocked(self, number_of_unlocked):
        self.unlocked_elements = number_of_unlocked
        self.unlocked_label.show()

    def set_titles(self, title1, title2=None):
        self.title_label1.set_text(title1)
        if self.title_label2 is not None and title2 is not None:
            self.title_label2.set_text(title2)

    def get_titles(self):
        title1 = self.title_label1.get_text()
        title2 = None
        if self.title_label2 is not None:
            title2 = self.title_label2.get_text()

        return (title1, title2)

