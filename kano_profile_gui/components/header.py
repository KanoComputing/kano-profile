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

        self.width = 734
        self.height = 44
        self.locked_elements = 5  # For now
        self.unlocked_elements = 5  # For now

        padlock_label_width = 60
        padlock_label_height = 44

        self.box = Gtk.Box()
        self.box.set_size_request(self.width, self.height)

        locked_pic = icons.set_from_name("locked")
        self.locked_label = Gtk.Label(": " + str(self.locked_elements))
        self.locked_label.get_style_context().add_class("padlock_label")
        locked_box = Gtk.Box()
        locked_box.pack_start(locked_pic, False, False, 0)
        locked_box.pack_start(self.locked_label, False, False, 0)
        locked_box.set_size_request(padlock_label_width, padlock_label_height)

        unlocked_pic = icons.set_from_name("unlocked")
        self.unlocked_label = Gtk.Label(": " + str(self.unlocked_elements))
        self.unlocked_label.get_style_context().add_class("padlock_label")
        unlocked_box = Gtk.Box()
        unlocked_box.pack_start(unlocked_pic, False, False, 0)
        unlocked_box.pack_start(self.unlocked_label, False, False, 0)
        unlocked_box.set_size_request(padlock_label_width, padlock_label_height)

        self.halign = Gtk.Alignment(xscale=0.0, yscale=0.0, xalign=0.5, yalign=0.5)
        self.halign.set_size_request(580, 44)

        self.title_label1 = Gtk.Label(title1.upper())
        self.title_label1.get_style_context().add_class("heading")

        self.title_label2 = None

        # If there are two titles, then we need to have 2 radio buttons to switch views
        if title2 is not None:
            self.radiobutton1 = self.create_button(title1.upper())
            self.radiobutton2 = self.create_button(self.radiobutton1, title2.upper())
            self.container = Gtk.Box()
            self.container.pack_start(self.radiobutton1, False, False, 0)
            self.container.pack_start(self.radiobutton2, False, False, 0)
            self.radiobutton1.set_active(True)
            self.radiobutton2.set_active(False)
            self.halign.add(self.container)

        else:
            self.halign.add(self.title_label1)

        self.box.pack_start(locked_box, False, False, 0)
        self.box.pack_start(self.halign, False, False, 0)
        self.box.pack_end(unlocked_box, False, False, 0)

    def set_locked_number(self, number_of_locked):
        self.locked_elements = number_of_locked
        self.locked_label.show()

    def set_unlocked_number(self, number_of_unlocked):
        self.unlocked_elements = number_of_unlocked
        self.unlocked_label.show()

    def set_titles(self, title1, title2=None):
        self.radiobutton1.set_label(title1)
        if self.radiobutton2 is not None and title2 is not None:
            self.radiobutton2.set_label(title2)

    def get_titles(self):
        title1 = self.radiobutton1.get_label()
        title2 = None
        if self.radiobutton2 is not None:
            title2 = self.radiobutton2.get_label()

        return (title1, title2)

    def create_button(self, title, widget=None):
        if widget is not None:
            button = Gtk.RadioButton.new_with_label_from_widget(title, widget)
        else:
            button = Gtk.RadioButton(title)
        button.set_size_request(297, 44)
        button.get_style_context().add_class("header_button")
        # This means we don'tdraw the radio button
        button.set_mode(False)
        button.get_child().get_style_context().add_class("heading")
        return button

    def set_event_listener1(self, callback):
        self.radiobutton1.connect("toggled", callback)
        #self.radiobutton1.connect("clicked", callback)

    def set_event_listener2(self, callback):
        self.radiobutton2.connect("toggled", callback)
        #self.radiobutton2.connect("clicked", callback)


