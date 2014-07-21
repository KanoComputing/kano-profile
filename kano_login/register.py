#!/usr/bin/env python

# register.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for register screen

import re
import os
import sys
from gi.repository import Gtk

from kano.logging import logger
from kano.utils import run_bg

from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.heading import Heading
from kano.gtk3.buttons import KanoButton, OrangeButton

from kano_profile.paths import bin_dir, legal_dir
from kano_profile.profile import save_profile_variable
from kano_world.functions import register as register_

from kano_login.templates.labelled_entries import LabelledEntries
from kano_login.templates.top_bar_template import TopBarTemplate
from kano_login.data import get_data


win = None
box = None
over_13 = True


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


class Register(TopBarTemplate):
    data_over_13 = get_data("REGISTER_OVER_13")
    data_under_13 = get_data("REGISTER_UNDER_13")

    def __init__(self, win, over_13=False):
        TopBarTemplate.__init__(self)

        self.win = win
        self.win.add(self)
        self.enable_prev()

        self.over_13 = over_13

        self.go_to_terms_conditions = OrangeButton("I accept the terms and conditions")
        self.checkbutton = Gtk.CheckButton()
        checkbox_box = Gtk.Box()
        checkbox_box.pack_start(self.checkbutton, False, False, 0)
        checkbox_box.pack_start(self.go_to_terms_conditions, False, False, 0)
        checkbox_align = Gtk.Alignment(xscale=0, xalign=0.5)
        checkbox_align.add(checkbox_box)

        self.checkbutton.connect("toggled", self.set_sensitive_toggled)
        self.go_to_terms_conditions.connect("button_press_event", self.show_terms_and_conditions)

        self.kano_button = KanoButton("REGISTER")
        self.kano_button.set_sensitive(False)
        self.kano_button.pack_and_align()
        self.kano_button.connect("button-release-event", self.register_user)
        self.kano_button.connect("key-press-event", self.register_user)

        if self.over_13:
            header = self.data_over_13["LABEL_1"]
            subheading = self.data_over_13["LABEL_2"]

        else:
            header = self.data_under_13["LABEL_1"]
            subheading = self.data_under_13["LABEL_2"]

        title = Heading(header, subheading)
        self.entries_container = LabelledEntries([{"heading": "Username", "subheading": ""}, {"heading": "Email", "subheading": ""}, {"heading": "Password", "subheading": "Min 6 chars"}])
        self.box.pack_start(title.container, False, False, 0)
        self.box.pack_start(self.entries_container, False, False, 10)
        self.box.pack_start(checkbox_align, False, False, 5)
        self.box.pack_start(self.kano_button.align, False, False, 10)

        entries = self.entries_container.get_entries()
        for entry in entries:
            entry.connect("key_release_event", self.set_sensitive_on_key_up)

        # password entry
        entry = entries[len(entries) - 1]
        entry.set_visibility(False)

        self.win.show_all()

    def show_terms_and_conditions(self, widget, event):
        self.checkbutton.set_active(True)

        legal_text = ''
        for file in os.listdir(legal_dir):
            with open(legal_dir + file, 'r') as f:
                legal_text = legal_text + f.read() + '\n\n\n'

        kdialog = KanoDialog("Terms and conditions", "", scrolled_text=legal_text)
        kdialog.run()

    def set_register_sensitive(self):
        entry_text = self.entries_container.get_entry_text()
        bool_value = True

        for text in entry_text:
            bool_value = bool_value and (text != "")

        if bool_value and self.checkbutton.get_active():
            self.kano_button.set_sensitive(True)
        else:
            self.kano_button.set_sensitive(False)

    def set_sensitive_toggled(self, widget):
        self.set_register_sensitive()

    def set_sensitive_on_key_up(self, widget, event):
        self.set_register_sensitive()

    def register_user(self, widget, event):

        if not hasattr(event, 'keyval') or event.keyval == 65293:
            entries = self.entries_container.get_entries()
            self.win.username = entries[0].get_text()
            self.win.email = entries[1].get_text()
            self.win.password = entries[2].get_text()

            logger.info('trying to register user')
            success, text = register_(self.win.email, self.win.username, self.win.password)

            if not success:
                logger.info('problem with registration: {}'.format(text))
                kdialog = KanoDialog("Houston, we have a problem", str(text))
                kdialog.run()

            else:
                logger.info('registration successful')

                save_profile_variable('gender', self.win.gender)
                save_profile_variable('birthdate', self.win.bday_date)

                # running kano-sync after registration
                logger.info('running kano-sync after successful registration')
                cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
                run_bg(cmd)

                sys.exit(0)

