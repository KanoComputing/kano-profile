#!/usr/bin/env python

# GetData.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import re
import os
import time
import datetime
from gi.repository import Gtk, GObject
from kano.utils import is_number
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano.gtk3.kano_dialog import KanoDialog
from kano_avatar.paths import CSS_PATH
from kano_profile.paths import legal_dir
from kano.logging import logger


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


class DataTemplate(Gtk.EventBox):
    __gsignals__ = {
        'widgets-filled': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'widget-empty': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.width = 250
        self.height = 350
        self.set_size_request(self.width, self.height)

        apply_styling_to_screen(CSS_PATH)
        self.get_style_context().add_class("data_screen")


class GetData2(DataTemplate):
    '''This first class registration box is to get
    the username, password and birthday
    '''

    def __init__(self):
        DataTemplate.__init__(self)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.email_entry = LabelledEntry("Email")
        self.email_entry.connect('key-release-event', self.widgets_full)

        self.guardian_email_entry = LabelledEntry("Guardian's Email (optional)")
        self.guardian_email_entry.connect('key-release-event', self.widgets_full)

        birthday_widget = self._create_birthday_widget()

        self.entries = [
            self.email_entry,
            self._day_entry,
            self._month_entry,
            self._year_entry
        ]

        box.pack_start(self.email_entry, False, False, 5)
        box.pack_start(self.guardian_email_entry, False, False, 5)
        box.pack_start(birthday_widget, False, False, 5)
        box.set_margin_top(20)

        self.add(box)

    def _create_birthday_widget(self):
        self._day_entry = Gtk.Entry()
        self._day_entry.set_size_request(50, -1)
        self._day_entry.set_width_chars(2)
        self._day_entry.set_placeholder_text("DD")
        self._day_entry.connect('key-release-event', self.widgets_full)

        self._month_entry = Gtk.Entry()
        self._month_entry.set_size_request(50, -1)
        self._month_entry.set_width_chars(2)
        self._month_entry.set_placeholder_text("MM")
        self._month_entry.connect('key-release-event', self.widgets_full)

        self._year_entry = Gtk.Entry()
        self._year_entry.set_size_request(70, -1)
        self._year_entry.set_width_chars(4)
        self._year_entry.set_placeholder_text("YYYY")
        self._year_entry.connect('key-release-event', self.widgets_full)

        hbox = Gtk.Box()
        hbox.pack_start(self._day_entry, False, False, 0)
        hbox.pack_start(self._month_entry, False, False, 20)
        hbox.pack_start(self._year_entry, False, False, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        birthday_label = Gtk.Label("Birthday", xalign=0)
        birthday_label.get_style_context().add_class("get_data_label")
        vbox.pack_start(birthday_label, False, False, 0)
        vbox.pack_start(hbox, False, False, 10)

        vbox.set_margin_left(30)

        return vbox

    def _get_birthday_data(self):
        bday_entries = [self._day_entry, self._month_entry, self._year_entry]
        bday = []

        for entry in bday_entries:
            is_valid_number, text = self._check_entry_is_number(entry)
            if not is_valid_number:
                return (False, {})
            else:
                bday.append(text)

        return (True, {'day': bday[0], 'month': bday[1], 'year': bday[2]})

    def get_data(self):
        data = {}

        data['email'] = self.email_entry.get_text()
        data['guardian_email'] = self.guardian_email_entry.get_text()

        bday_data = self._get_birthday_data()[1]
        data.update(bday_data)

        return data

    def widgets_full(self, widget, event):
        full = True

        for entry in self.entries:
            text = entry.get_text()
            if not text:
                full = False
            elif entry == self.email_entry:
                full = is_email(text)

        if full:
            self.emit('widgets-filled')
        else:
            self.emit('widget-empty')

    def calculate_age(self):
        # Error messages
        default_error = "Oops!"
        default_desc = "You haven't entered a valid birthday"
        entry_not_valid = "You haven't entered a valid number"

        try:
            # boolean, dictionary
            valid_bday, bday = self._get_birthday_data()
            if not valid_bday:
                raise Exception(default_error, entry_not_valid)

            logger.debug("User birthday = {}".format(bday))

            bday_date = str(datetime.date(bday["year"],
                                          bday["month"],
                                          bday["day"]))

            # To allow people to enter their year as a two digit number
            if bday["year"] < 15 and bday["year"] >= 0:
                bday["year"] = bday["year"] + 2000
            elif bday["year"] >= 15 and bday["year"] <= 99:
                bday['year'] = bday['year'] + 1900

            # Get current date
            current_day = int(time.strftime("%d"))
            current_month = int(time.strftime("%m"))
            current_year = int(time.strftime("%Y"))

            age = current_year - bday['year']
            logger.debug("User age = {}".format(age))

            if age < 0 or age > 114:
                raise Exception(default_error, default_desc)

            if current_month < bday['month']:
                age = age - 1
            elif current_month == bday['month']:
                if current_day < bday['day']:
                    age = age - 1
                # TODO: if it's their birthday, do something special?
                # elif current_day == bday_day:
                #    print "IT'S YOUR BIIIIRTHDAY"
            return age, bday_date, ()

        except Exception as e:

            if len(e.args) == 1:
                error1 = default_error
                error2 = "There's a problem - {0}".format(e)

            elif len(e.args) == 2:
                error1 = e[0]
                error2 = e[1]

            else:
                error1 = default_error
                error2 = default_desc

            return -1, -1, (error1, error2)

    def _check_entry_is_number(self, entry):
        entry_text = entry.get_text()
        if not is_number(entry_text):
            return False, ''

        return True, int(entry_text)


class GetData3(DataTemplate):
    '''This second class registration box is to get the email,
    optional guardian's email and show the terms and conditions.
    '''
    __gsignals__ = {
        'terms-and-conditions': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        DataTemplate.__init__(self)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.username_entry = LabelledEntry("Username")
        self.username_entry.connect('key-release-event', self.widgets_full)

        self.password_entry = LabelledEntry("Password - min. 6 letters")
        self.password_entry.connect('key-release-event', self.widgets_full)
        self.password_entry.set_visibility(False)

        self.entries = [
            self.username_entry,
            self.password_entry
        ]

        self.checkbutton = Gtk.CheckButton()
        self.checkbutton.get_style_context().add_class("get_data_checkbutton")
        self.checkbutton.set_size_request(50, 50)
        self.checkbutton.connect('toggled', self.widgets_full)
        self.checkbutton.set_margin_left(30)

        self.tc_button = OrangeButton("I agree to the terms and\nconditions")
        self.tc_button.connect("clicked", self._emit_t_and_c_signal)

        hbox = Gtk.Box()
        hbox.pack_start(self.checkbutton, False, False, 0)
        hbox.pack_start(self.tc_button, False, False, 0)

        box.pack_start(self.username_entry, False, False, 10)
        box.pack_start(self.password_entry, False, False, 10)
        box.pack_start(hbox, False, False, 10)

        box.set_margin_top(20)

        self.add(box)

    def disable_all(self):
        self.checkbutton.set_sensitive(False)
        self.username_entry.set_sensitive(False)
        self.password_entry.set_sensitive(False)
        self.tc_button.set_sensitive(False)

    def enable_all(self):
        self.checkbutton.set_sensitive(True)
        self.username_entry.set_sensitive(True)
        self.password_entry.set_sensitive(True)
        self.tc_button.set_sensitive(True)

    def _emit_t_and_c_signal(self, widget):
        self.emit("terms-and-conditions")

    def get_data(self):
        data = {}

        data['username'] = self.username_entry.get_text()
        data['password'] = self.password_entry.get_text()

        return data

    def widgets_full(self, widget=None, event=None):
        full = True

        for entry in self.entries:
            if not entry.get_text():
                full = False

        checked = self.checkbutton.get_active()

        if checked and full:
            self.emit('widgets-filled')
        else:
            self.emit('widget-empty')


class LabelledEntry(Gtk.Box):
    '''Produces a labelled entry, suitable for the registration screens
    '''

    def __init__(self, text):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self._label = Gtk.Label(text, xalign=0)
        self._label.get_style_context().add_class("get_data_label")
        self.pack_start(self._label, False, False, 0)

        self._entry = Gtk.Entry()
        self._entry.get_style_context().add_class("get_data_entry")
        self._entry.set_size_request(200, -1)
        self.pack_start(self._entry, False, False, 10)

        self.set_margin_right(80)
        self.set_margin_left(30)

    def set_visibility(self, value):
        return self._entry.set_visibility(value)

    def get_text(self):
        return self._entry.get_text()

    def get_label_text(self):
        return self._label.get_text()
