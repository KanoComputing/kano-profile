#!/usr/bin/env python

# GetData.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano.gtk3.buttons import OrangeButton


class GetData1(Gtk.EventBox):
    '''This first class registration box is to get
    the username, password and birthday
    '''

    def __init__(self):
        Gtk.EventBox.__init__(self)

        # TODO: Repeated
        self.width = 400
        self.height = 500
        self.set_size_request(self.width, self.height)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        username_entry = LabelledEntry("Username")
        password_entry = LabelledEntry("Password - min. 6 letters")
        age_entry = LabelledEntry("Age")

        box.pack_start(username_entry, False, False, 0)
        box.pack_start(password_entry, False, False, 0)
        box.pack_start(age_entry, False, False, 0)

        self.add(box)


class GetData2(Gtk.EventBox):
    '''This second class registration box is to get the email,
    optional guardian's email and show the terms and conditions.
    '''

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.width = 400
        self.height = 500
        self.set_size_request(self.width, self.height)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        email_entry = LabelledEntry("Email")
        guardian_email_entry = LabelledEntry("Guardian's Email (optional)")

        # Terms and conditions check button
        checkbutton = Gtk.CheckButton()
        checkbutton.get_style_context().add_class("get_data_checkbutton")
        tc_button = OrangeButton("I agree to the terms and conditions")
        tc_button.connect("clicked", self.launch_t_and_cs)
        hbox = Gtk.Box()
        hbox.pack_start(checkbutton, False, False, 0)
        hbox.pack_start(tc_button, False, False, 0)

        box.pack_start(email_entry, False, False, 0)
        box.pack_start(guardian_email_entry, False, False, 0)
        box.pack_start(hbox, False, False, 0)

        self.add(box)

    def launch_t_and_cs(self, widget):
        # TODO: find out how to launch this.  Dialog?
        print "launch terms and conditions"


class LabelledEntry(Gtk.Box):
    '''Produces a labelled entry, suitable for the registration screens
    '''

    def __init__(self, text):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self._label = Gtk.Label(text)
        self._label.get_style_context().add_class("get_data_label")
        self.pack_start(self._label, False, False, 0)

        self._entry = Gtk.Entry()
        self._entry.get_style_context().add_class("get_data_entry")
        self.pack_start(self._entry, False, False, 0)

    def get_entry_text(self):
        return self._entry.get_text()

    def get_label_text(self):
        return self._label.get_text()
