#!/usr/bin/env python

# about_you.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set age and gender of user

#from gi.repository import Gtk

import re
from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano_login import register
from kano_login.labelled_entries import LabelledEntries


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


class PermissionSlip():
    def __init__(self, win, box):

        self.win = win
        self.box = box

        title = Heading("Permission Slip", "Add a parent's or teacher's email")

        self.entries_container = LabelledEntries([{"heading": "Email", "subheading": ""}, {"heading": "Confirm Email", "subheading": ""}])

        # set callbacks to the entries
        entry1 = self.entries_container.get_entry(1)
        entry1.connect("key-release-event", self.set_button_sensitivity)

        self.next_button = KanoButton("NEXT")
        self.next_button.pack_and_align()
        self.next_button.set_sensitive(False)
        self.next_button.connect("button-release-event", self.send_email)

        self.box.pack_start(title.container, False, False, 0)
        self.box.pack_start(self.entries_container, False, False, 30)
        self.box.pack_start(self.next_button.align, False, False, 0)

        self.box.show_all()

    def set_button_sensitivity(self, widget, event):

        emails = self.entries_container.get_entry_text()

        if emails[0] == emails[1] and is_email(emails[0]):
            self.next_button.set_sensitive(True)

    def send_email(self, widget, event):

        emails = self.entries_container.get_entry_text()

        if emails[0] == emails[1]:
            self.win.email = emails[0]

            # send email
            # Launch dialog if unsuccessful?
            # else...
            self.win.clear_box()
            register.activate(self.win, self.box)
