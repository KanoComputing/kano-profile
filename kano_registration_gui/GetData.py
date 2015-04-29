#!/usr/bin/env python

# GetData.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import re
from gi.repository import Gtk, GObject
from kano.gtk3.kano_dialog import KanoDialog
from kano_profile.paths import legal_dir
from kano_registration_gui.data_functions import (
    get_cached_data, cache_data, cache_emails
)
from kano_registration_gui.BirthdayWidget import BirthdayWidget
from kano_registration_gui.LabelledEntry import LabelledEntry
from kano_registration_gui.TermsAndConditions import TermsAndConditions

from kano.logging import logger
from email.utils import parseaddr


def is_email(email):
    if '@' in parseaddr(email)[1]:
        return True
    else:
        return False


def check_username(username):
    '''Check username only has letters, numbers, - and _
    '''
    pattern = '[a-zA-Z0-9_\-.]'
    num_matches = len(re.split(pattern, username))
    if num_matches == len(username) + 1 and \
            len(username) >= 3 and \
            len(username) <= 25:
        return True
    else:
        return False


class DataTemplate(Gtk.EventBox):
    __gsignals__ = {
        'widgets-filled': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'widgets-empty': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.width = 250
        self.height = 350
        self.set_size_request(self.width, self.height)
        self.get_style_context().add_class("data_screen")


class GetData2(DataTemplate):
    '''This second class registration box is to get the username,
    password and birthday of the user.
    '''

    def __init__(self):
        DataTemplate.__init__(self)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # This data contains the saved username and birthday
        data = self.get_cached_username_and_birthday()

        self.username_entry = LabelledEntry("Username", data["username"])
        self.username_entry.connect("key-release-event", self.validate_username)
        logger.debug("Checking for internet")

        # Do not fill this in
        self.password_entry = LabelledEntry("Password")
        self.password_entry.connect("key-release-event", self.validate_password)
        self.bday_widget = BirthdayWidget(
            data['birthday_day'],
            data['birthday_month'],
            data['birthday_year']
        )

        self.validate_username()

        self.bday_widget.connect("bday-key-release-event", self.widgets_full)
        box.pack_start(self.username_entry, False, False, 10)
        box.pack_start(self.password_entry, False, False, 10)
        box.pack_start(self.bday_widget, False, False, 0)

        box.set_margin_top(20)

        self.add(box)

    def validate_password(self, widget=None, event=None):
        '''widget is the password entry
        '''
        password = self.password_entry.get_text()
        if len(password) == 0:
            self.password_entry.label_success("")
        elif len(password) < 6:
            self.password_entry.label_success("is too short", "fail")
        else:
            self.password_entry.label_success("looks good!", "success")

        self.widgets_full()

    def validate_username(self, widget=None, event=None):
        '''widget is the username entry as is conencted to the key-release-event
        '''

        username = self.username_entry.get_text()
        if len(username) == 0:
            self.username_entry.label_success("")
        elif check_username(username):
            self.username_entry.label_success("is valid", "success")
        else:
            self.username_entry.label_success("is invalid", "fail")

        self.widgets_full()

    def calculate_age(self):
        return self.bday_widget.calculate_age()

    def enable_all(self):
        self.checkbutton.set_sensitive(True)
        self.username_entry.set_sensitive(True)
        self.password_entry.set_sensitive(True)
        self.tc_button.set_sensitive(True)

    def get_entry_data(self):
        data = {}

        data['username'] = self.username_entry.get_text()
        data['password'] = self.password_entry.get_text()

        bday_data = self.bday_widget.get_birthday_data()[1]
        data.update(bday_data)

        data['age'] = self.bday_widget.calculate_age()

        logger.debug("data from data screen 1 {}".format(data))
        return data

    # To be passed to the registration screen
    def save_username_and_birthday(self):
        data = self.get_entry_data()
        cache_data("username", data['username'])
        cache_data("birthday_day", data['day'])
        cache_data("birthday_month", data['month'])
        cache_data("birthday_year", data['year'])

    def get_cached_username_and_birthday(self):
        username = get_cached_data("username")
        birthday_day = get_cached_data("birthday_day")
        birthday_month = get_cached_data("birthday_month")
        birthday_year = get_cached_data("birthday_year")
        return {
            "username": username,
            "birthday_day": birthday_day,
            "birthday_month": birthday_month,
            "birthday_year": birthday_year
        }

    def widgets_full(self, widget=None, event=None):
        full = True

        if not self.username_entry.validated:
            full = False

        if not self.password_entry.validated:
            full = False

        bday_filled = self.bday_widget.birthday_entries_filled()

        if full and bday_filled:
            logger.debug("emiting widgets-full")
            self.emit('widgets-filled')
        else:
            logger.debug("emiting widgets-empty")
            self.emit('widgets-empty')


class GetData3(DataTemplate):
    '''This first class registration box is to get
    the username, password and birthday
    '''

    def __init__(self, age):
        DataTemplate.__init__(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        email = get_cached_data("email")
        secondary_email = get_cached_data("secondary_data")

        self.t_and_cs = TermsAndConditions()
        self.t_and_cs.checkbutton.connect("clicked", self.widgets_full)
        self.t_and_cs.connect("t-and-cs-clicked",
                              self.show_terms_and_conditions)

        # If the user is younger than 14, ask for both Guardian and
        # user email, but the guardian email is compulsory
        if age <= 13:
            self.email_entry = LabelledEntry(
                "Parent's Email (required)", email
            )
            self.email_entry.connect('key-release-event',
                                     self.widgets_full)

            self.secondary_email_entry = LabelledEntry(
                "Your Email (optional)", secondary_email
            )
            self.secondary_email_entry.connect(
                'key-release-event', self.widgets_full
            )

            box.pack_start(self.email_entry, False, False, 5)
            box.pack_start(self.secondary_email_entry, False, False, 5)

        # Otherwise, there is only one compulsory email
        else:
            self.email_entry = LabelledEntry("Your Email (required)", email)
            self.email_entry.connect('key-release-event', self.widgets_full)
            self.secondary_email_entry = None
            box.pack_start(self.email_entry, False, False, 5)

        self.entries = [self.email_entry]

        box.pack_start(self.t_and_cs, False, False, 5)
        box.set_margin_top(20)

        self.add(box)

    def disable_all(self):
        self.email_entry.set_sensitive(False)

        if self.secondary_email_entry:
            self.secondary_email_entry.set_sensitive(False)
        self.t_and_cs.disable_all()

    def enable_all(self):
        self.email_entry.set_sensitive(True)

        if self.secondary_email_entry:
            self.secondary_email_entry.set_sensitive(True)
        self.t_and_cs.enable_all()

    def get_email_entry_data(self):
        data = {}

        data['email'] = self.email_entry.get_text()
        if self.secondary_email_entry:
            data['secondary_email'] = self.secondary_email_entry.get_text()
        else:
            data['secondary_email'] = ""

        # Cache emails if they are retrieved
        cache_emails(data["email"], data["secondary_email"])

        return data

    def cache_emails(self):
        data = self.get_email_entry_data()
        cache_emails(data["email"], data["secondary_email"])

    def widgets_full(self, widget=None, event=None):

        full = True

        for entry in self.entries:
            text = entry.get_text()
            if not text:
                full = False
            elif entry == self.email_entry or \
                    entry == self.guardian_email_entry:
                full = is_email(text)

        if not self.t_and_cs.is_checked():
            full = False

        if full:
            self.emit('widgets-filled')
        else:
            self.emit('widgets-empty')

    def show_terms_and_conditions(self, widget):
        '''This is the dialog containing the terms and conditions - same as
        shown before creating an account
        '''
        window = widget.get_toplevel()

        legal_text = ''
        for file in os.listdir(legal_dir):
            with open(legal_dir + file, 'r') as f:
                legal_text = legal_text + f.read() + '\n\n\n'

        kdialog = KanoDialog("Terms and conditions", "",
                             scrolled_text=legal_text,
                             parent_window=window)
        kdialog.run()
