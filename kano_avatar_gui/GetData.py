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
from kano_profile_gui.components.icons import get_ui_icon
from kano_world.connection import request_wrapper
from kano_avatar_gui.BirthdayWidget import BirthdayWidget
from kano_avatar_gui.LabelledEntry import LabelledEntry
from kano_avatar_gui.TermsAndConditions import TermsAndConditions

from kano.logging import logger
from kano_profile.apps import load_app_state_variable, save_app_state_variable


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


def does_user_exist(username):
    '''username is the string of the username which we want to see
    is registered.
    If return True, exists,
    If return False, does not exist
    May return None, in which case not sure?
    '''
    user_request = "/users/username/{}".format(username)
    success, text, data = request_wrapper('get', user_request)
    if success:
        return True
    elif not success and text == "User not found":
        return False

    # Could have failed because of bad internet connection, or server timed
    # out.  Inconclusive.
    return None


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

    def cache_data(self, category, value):
        save_app_state_variable("kano-avatar-registration", category, value)

    def get_cached_data(self, category):
        return load_app_state_variable("kano-avatar-registration", category)


class GetData2(DataTemplate):
    '''This second class registration box is to get the email,
    optional guardian's email and show the terms and conditions.
    '''

    def __init__(self):
        DataTemplate.__init__(self)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        (username, birthday_day, birthday_month, birthday_year) = self.get_cached_username_and_birthday()
        self.username_entry = LabelledEntry("Username", username)
        self.username_entry.connect('labelled-entry-key-release', self.widgets_full)
        # Get data about whether to fill this in.

        # This doesn't work because the parent window doesn't exist yet
        # window = self.username_entry.get_parent_window()
        # window.set_events(Gdk.EventType.FOCUS_CHANGE)
        # self.username_entry.connect('key-release-event', self.widgets_full)

        # If there is internet, link the focus out event to checking the
        # username
        logger.debug("Checking for internet")

        '''
        if is_internet():
            logger.debug("Attaching check username wrapper to username entry")
            # Check the username is valid when we focus out of the entry
            self.username_entry.connect('focus-out-event', self.check_username_wrapper)
        '''

        # Do not fill this in
        self.password_entry = LabelledEntry("Password - min. 6 letters")
        self.password_entry.connect('labelled-entry-key-release', self.widgets_full)
        self.password_entry.set_visibility(False)

        self.entries = [
            self.username_entry,
            self.password_entry
        ]

        self.bday_widget = BirthdayWidget(birthday_day, birthday_month, birthday_year)
        self.bday_widget.connect("bday-key-release-event", self.widgets_full)
        # self.bday_widget.connect("bday-widgets-empty", )

        box.pack_start(self.username_entry, False, False, 10)
        box.pack_start(self.password_entry, False, False, 10)
        box.pack_start(self.bday_widget, False, False, 0)

        box.set_margin_top(20)

        self.add(box)

    ############################################
    # Not used

    def check_username_wrapper(self, widget, event):
        logger.debug("Hitting username wrapper")
        username = widget.get_text()
        logger.debug("username = {}".format(username))
        self.check_username(username)

    def check_username(self, username):
        '''Check if the username is valid.
        If it is, add a tick icon, otherwise add a cross icon.
        '''
        logger.debug("Entered check_username")
        user_exists = does_user_exist(username)

        if user_exists:
            # pack tick into the entry
            tick_icon = get_ui_icon("tick")
            self.username_entry.set_icon_from_pixbuf(tick_icon)

        elif user_exists is False:
            tick_icon = get_ui_icon("cross")
            self.username_entry.set_icon_from_pixbuf(tick_icon)

        else:
            # show dialog?
            print "Not sure if the user exists"

    ################################################

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

    def save_username_and_birthday(self):
        data = self.get_entry_data()
        self.cache_data("username", data['username'])
        self.cache_data("birthday_day", data['day'])
        self.cache_data("birthday_month", data['month'])
        self.cache_data("birthday_year", data['year'])

    def get_cached_username_and_birthday(self):
        username = self.get_cached_data("username")
        birthday_day = self.get_cached_data("birthday_day")
        birthday_month = self.get_cached_data("birthday_month")
        birthday_year = self.get_cached_data("birthday_year")
        return (username, birthday_day, birthday_month, birthday_year)

    def widgets_full(self, widget=None, event=None):
        logger.debug("widgets-full in GetData hit")

        full = True

        for entry in self.entries:
            if not entry.get_text():
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

    def __init__(self):
        DataTemplate.__init__(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        email, guardian_email = self.get_cached_emails()

        self.email_entry = LabelledEntry("Email", email)
        self.email_entry.connect('key-release-event', self.widgets_full)
        self.guardian_email_entry = LabelledEntry(
            "Guardian's Email (optional)", guardian_email
        )
        self.guardian_email_entry.connect('key-release-event', self.widgets_full)

        self.t_and_cs = TermsAndConditions()
        self.t_and_cs.checkbutton.connect("clicked", self.widgets_full)
        self.t_and_cs.connect("t-and-cs-clicked", self.show_terms_and_conditions)

        # This might need to change
        self.entries = [
            self.email_entry
        ]

        box.pack_start(self.email_entry, False, False, 5)
        box.pack_start(self.guardian_email_entry, False, False, 5)
        box.pack_start(self.t_and_cs, False, False, 5)
        box.set_margin_top(20)

        self.add(box)

    def disable_all(self):
        self.email_entry.set_sensitive(False)
        self.guardian_email_entry.set_sensitive(False)
        self.t_and_cs.disable_all()

    def enable_all(self):
        self.email_entry.set_sensitive(True)
        self.guardian_email_entry.set_sensitive(True)
        self.t_and_cs.enable_all()

    def cache_emails(self):
        email_address = self.email_entry.get_text()
        self.cache_data("email", email_address)

        guardian_email_address = self.guardian_email_entry.get_text()
        self.cache_data("gurdian_email", guardian_email_address)

    def get_cached_emails(self):
        email = self.get_cached_data("email")
        guardian_email = self.get_cached_data("guardian_email")
        return (email, guardian_email)

    def get_entry_data(self):
        data = {}

        data['email'] = self.email_entry.get_text()
        data['guardian_email'] = self.guardian_email_entry.get_text()

        return data

    def widgets_full(self, widget=None, event=None):

        full = True

        for entry in self.entries:
            text = entry.get_text()
            if not text:
                full = False
            elif entry == self.email_entry:
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
