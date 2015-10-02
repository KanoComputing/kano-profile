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
from kano_registration_gui.cache_functions import (
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
    pattern = '^[a-zA-Z0-9_\-.]+$'
    match = re.match(pattern, username)
    return match and len(username) >= 3 and len(username) <= 25


def check_password(password):
    '''Check password contains no whitespace and is minimum

    '''
    pattern = '^\S+$'
    match = re.match(pattern, password)
    return match and len(password) > 5


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


class GetData1(DataTemplate):
    '''This second class registration box is to get the username,
    password and birthday of the user.
    '''

    def __init__(self):
        DataTemplate.__init__(self)

        # Set the birthday to be False by default
        self._is_birthday_valid = False
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # This data contains the saved username and birthday
        data = self.get_cached_username_and_birthday()

        self._username = LabelledEntry("Username", data["username"])
        self._username.connect("key-release-event", self.validate_username)
        logger.debug("Checking for internet")

        # Do not fill this in
        self._password = LabelledEntry(_("Password"))
        self._password.connect("key-release-event", self.validate_password)

        self.bday_widget = BirthdayWidget(
            data['birthday_day'],
            data['birthday_month'],
            data['birthday_year']
        )
        self.bday_widget.connect('birthday-valid', self._birthday_valid)
        self.bday_widget.connect('birthday-invalid', self._birthday_invalid)

        self.update_birthday_widget_from_cache()
        self.validate_username()

        self.show_password = Gtk.CheckButton.new_with_label(_("Show password"))
        self.show_password.get_style_context().add_class("show_password")
        self.show_password.connect("toggled", self.make_password_entry_visible)
        self.show_password.set_active(True)
        self.show_password.set_margin_left(30)

        self.bday_widget.connect("bday-key-release-event", self.widgets_full)
        box.pack_start(self._username, False, False, 15)
        box.pack_start(self._password, False, False, 5)
        box.pack_start(self.show_password, False, False, 0)
        box.pack_start(self.bday_widget, False, False, 15)

        box.set_margin_top(20)

        self.add(box)

    @property
    def username(self):
        return self._username

    def make_password_entry_visible(self, widget):
        visibility = self.show_password.get_active()
        self._password.set_visibility(visibility)

    def validate_password(self, widget=None, event=None):
        '''widget is the password entry
        '''
        password = self._password.get_text()
        if len(password) == 0:
            self._password.label_success("")
        elif check_password(password):
            self._password.label_success(_("looks good!"), "success")
        else:
            self._password.label_success(_("is not valid"), "fail")

        self.widgets_full()

    def validate_username(self, widget=None, event=None):
        username = self._username.get_text()
        if len(username) == 0:
            self._username.label_success("")
        elif check_username(username):
            self._username.label_success(_(""), "success")
        else:
            self._username.label_success(_("is invalid"), "fail")

        self.widgets_full()

    def _birthday_valid(self, widget=None, event=None):
        self._is_birthday_valid = True
        self.widgets_full()

    def _birthday_invalid(self, widget=None, event=None):
        self._is_birthday_valid = False
        self.widgets_full()

    def calculate_age(self):
        return self.bday_widget.calculate_age()

    def enable_all(self):
        self.checkbutton.set_sensitive(True)
        self._username.set_sensitive(True)
        self._password.set_sensitive(True)
        self.tc_button.set_sensitive(True)

    def get_widget_data(self):
        data = {}

        data['username'] = self._username.get_text()
        data['password'] = self._password.get_text()

        bday_data = self.bday_widget.get_birthday_data()
        data.update(bday_data)

        data['age'] = self.bday_widget.calculate_age()

        logger.debug("data from data screen 1 {}".format(data))
        return data

    # To be passed to the registration screen
    def save_username_and_birthday(self):

        # Birthday should not strictly be got in entry data
        data = self.get_widget_data()

        cache_data("username", data['username'])
        cache_data("birthday_day", data['day'])
        cache_data("birthday_day_index", data["day_index"])
        cache_data("birthday_month", data['month'])
        cache_data("birthday_month_index", data["month_index"])
        cache_data("birthday_year", data['year'])
        cache_data("birthday_year_index", data["year_index"])

    def update_birthday_widget_from_cache(self):
        self.bday_widget.set_birthday_data(
            get_cached_data("birthday_year_index"),
            get_cached_data("birthday_month_index"),
            get_cached_data("birthday_day_index")
        )

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
        if (self._username.validated and
                self._password.validated and
                self._is_birthday_valid):
            logger.debug("emitting widgets-full")
            self.emit('widgets-filled')
        else:
            logger.debug("emitting widgets-empty")
            self.emit('widgets-empty')


class GetData2(DataTemplate):
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

        marketing_container = self._create_marketing_checkbox()
        marketing_enabled = get_cached_data("marketing_enabled")

        if marketing_enabled is not None:
            self.marketing_checkbutton.set_active(marketing_enabled)
        else:
            self.marketing_checkbutton.set_active(True)

        # If the user is younger than 14, ask for both Guardian and
        # user email, but the guardian email is compulsory
        if age <= 13:
            self.email_entry = LabelledEntry(
                _("Parent's Email (required)"), email
            )
            self.email_entry.connect('key-release-event',
                                     self.widgets_full)

            self.secondary_email_entry = LabelledEntry(
                _("Your Email (optional)"), secondary_email
            )
            self.secondary_email_entry.connect(
                'key-release-event', self.widgets_full
            )

            box.pack_start(self.email_entry, False, False, 5)
            box.pack_start(self.secondary_email_entry, False, False, 5)

        # Otherwise, there is only one compulsory email
        else:
            self.email_entry = LabelledEntry(_("Your Email (required)"), email)
            self.email_entry.connect('key-release-event', self.widgets_full)
            self.secondary_email_entry = None
            box.pack_start(self.email_entry, False, False, 5)

        self.entries = [self.email_entry]

        box.pack_start(self.t_and_cs, False, False, 10)
        box.pack_start(marketing_container, False, False, 0)
        box.set_margin_top(20)

        self.add(box)


    def _create_marketing_checkbox(self):
        self.marketing_checkbutton = Gtk.CheckButton()
        self.marketing_checkbutton.get_style_context().add_class(
            "get_data_checkbutton")
        self.marketing_checkbutton.set_margin_left(30)

        marketing_label = Gtk.Label(_("Email me cool stuff to do with my Kano"))
        marketing_label.set_max_width_chars(20)
        marketing_label.set_line_wrap(True)

        marketing_container = Gtk.Box()
        marketing_container.pack_start(self.marketing_checkbutton,
                                       False, False, 0)
        marketing_container.get_style_context().add_class(
            "get_data_checkbutton")
        marketing_container.pack_start(marketing_label, False, False, 0)

        return marketing_container

    def disable_all(self):
        self.email_entry.set_sensitive(False)

        if self.secondary_email_entry:
            self.secondary_email_entry.set_sensitive(False)
        self.t_and_cs.disable_all()
        self.marketing_checkbutton.set_sensitive(False)

    def enable_all(self):
        self.email_entry.set_sensitive(True)

        if self.secondary_email_entry:
            self.secondary_email_entry.set_sensitive(True)
        self.t_and_cs.enable_all()
        self.marketing_checkbutton.set_sensitive(True)

    def get_email_entry_data(self):
        '''This is the data that is sent to the main window and the
        registration
        '''

        data = {}

        data['email'] = self.email_entry.get_text()
        if self.secondary_email_entry:
            data['secondary_email'] = self.secondary_email_entry.get_text()
        else:
            data['secondary_email'] = ""

        data["marketing_enabled"] = self.marketing_checkbutton.get_active()

        # Cache emails if they are retrieved
        cache_emails(data["email"], data["secondary_email"], data["marketing_enabled"])

        return data

    def cache_emails(self):
        data = self.get_email_entry_data()
        cache_emails(data["email"], data["secondary_email"])

    def cache_marketing_choice(self):
        data = self.marketing_checkbutton.get_active()
        cache_data("marketing_enabled", data)

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

        # TODO: Figure out how/whether the legal text will be translated
        legal_text = ''
        for file in os.listdir(legal_dir):
            with open(legal_dir + file, 'r') as f:
                legal_text = legal_text + f.read() + '\n\n\n'

        kdialog = KanoDialog(_("Terms and conditions"), "",
                             scrolled_text=legal_text,
                             parent_window=window)
        kdialog.run()
