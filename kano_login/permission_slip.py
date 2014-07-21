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
from kano_login.register import Register
from kano_login.templates.labelled_entries import LabelledEntries
from kano_login.data import get_data
from kano_login.templates.top_bar_template import TopBarTemplate


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


class PermissionSlip(TopBarTemplate):
    data = get_data("PERMISSION_SLIP")

    def __init__(self, win):
        TopBarTemplate.__init__(self, "Permission Slip")

        self.win = win
        self.win.add(self)
        self.enable_prev()

        # get data
        header = self.data["LABEL_1"]
        description = self.data["LABEL_2"]
        kano_button_label = self.data["KANO_BUTTON"]

        title = Heading(header, description)

        self.entries_container = LabelledEntries([{"heading": "Email", "subheading": ""}, {"heading": "Confirm Email", "subheading": ""}])
        self.entries_container.set_spacing(15)

        # set callbacks to the entries
        for entry in self.entries_container.get_entries():
            entry.connect("key-release-event", self.set_button_sensitivity)

        self.next_button = KanoButton(kano_button_label)
        self.next_button.pack_and_align()
        self.next_button.set_sensitive(False)
        self.next_button.connect("button-release-event", self.send_email)

        self.box.pack_start(title.container, False, False, 10)
        self.box.pack_start(self.entries_container, False, False, 15)
        self.box.pack_start(self.next_button.align, False, False, 30)

        self.win.show_all()

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
            self.win.clear_win()
            Register(self.win, False)

        else:
            pass
            # Launch dialog
