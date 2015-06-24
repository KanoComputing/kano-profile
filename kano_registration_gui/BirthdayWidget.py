#!/usr/bin/env python

# BirthdayWidget.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, GObject
import time
import datetime
from kano.logging import logger
from kano.utils import is_number


class BirthdayWidget(Gtk.Box):

    __gsignals__ = {
        'bday-key-release-event': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'birthday-valid': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'birthday-invalid': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    FIELD_INCOMPLETE = 0
    NOT_A_NUMBER = -1

    def __init__(self, day=None, month=None, year=None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self._create_birthday_widget(day, month, year)

    def _create_birthday_widget(self, day=None, month=None, year=None):
        # TODO: Establish how DD, MM, YYYY should be translated
        self._day_entry = self._create_entry("DD", 60, 2, day)
        self._month_entry = self._create_entry("MM", 60, 2, month)
        self._year_entry = self._create_entry("YYYY", 70, 4, year)

        self._day_entry.connect('key-release-event', self.validate)
        self._month_entry.connect('key-release-event', self.validate)
        self._year_entry.connect('key-release-event', self.validate)

        label1 = self._create_separater_label()
        label2 = self._create_separater_label()

        hbox = Gtk.Box()
        hbox.pack_start(self._year_entry, False, False, 0)
        hbox.pack_start(label1, False, False, 0)
        hbox.pack_start(self._month_entry, False, False, 0)
        hbox.pack_start(label2, False, False, 0)
        hbox.pack_start(self._day_entry, False, False, 0)

        label_box = Gtk.Box()

        birthday_label = Gtk.Label(_("Birthday"))
        birthday_label.get_style_context().add_class("get_data_label")
        label_box.pack_start(birthday_label, False, False, 0)

        self._birthday_status = Gtk.Label()
        self._birthday_status.get_style_context().add_class("validation_label")
        label_box.pack_start(self._birthday_status, False, False, 0)

        self.pack_start(label_box, False, False, 0)
        self.pack_start(hbox, False, False, 0)

        self.set_margin_left(30)

    def _create_entry(self, placeholder_text, width=60, char_num=2, entry_text=None):
        entry = Gtk.Entry()

        entry.set_size_request(width, -1)

        entry.set_width_chars(char_num)
        entry.set_max_length(char_num)
        entry.set_placeholder_text(placeholder_text)
        entry.get_style_context().add_class("get_data_entry")
        entry.connect("key-release-event", self._emit_key_press)

        if entry_text:
            entry.set_text(str(entry_text))

        return entry

    def validate(self, *dummy):
        day = self._str_to_int(self._day_entry.get_text())
        month = self._str_to_int(self._month_entry.get_text())
        year = self._str_to_int(self._year_entry.get_text())

        if self.FIELD_INCOMPLETE in [day, month, year]:
            return self._set_validation_msg('', False)

        if self.NOT_A_NUMBER in [day, month, year]:
            return self._set_validation_msg(_('must be a number'), False)

        try:
            birthday = datetime.date(year, month, day)
        except Exception as e:
            return self._set_validation_msg(_(e.message), False)

        today = datetime.date.today()
        if birthday > today:
            return self._set_validation_msg(_('date is in the future'), False)

        oldest_date = today.replace(year=(today.year - 100))
        if birthday < oldest_date and (birthday.year < 0 or birthday.year > 99):
            return self._set_validation_msg(_('year out of range'), False)

        return self._set_validation_msg(_('is valid'), True)


    def _str_to_int(self, string):
        if len(string) == 0:
            return self.FIELD_INCOMPLETE

        if not string.isdigit():
            return self.NOT_A_NUMBER

        return int(string)


    def _set_validation_msg(self, message, valid):
        label = self._birthday_status
        style = label.get_style_context()

        style.remove_class('fail')
        style.remove_class('success')

        if valid:
            style.add_class('success')
            self.emit('birthday-valid')
        else:
            style.add_class('fail')
            self.emit('birthday-invalid')

        self._birthday_status.set_text(message)


    def _emit_key_press(self, widget, event):
        self.emit("bday-key-release-event")

    def birthday_entries_filled(self):
        rv = (
            self._year_entry.get_text() is not "" and
            self._month_entry.get_text() is not "" and
            self._day_entry.get_text() is not ""
        )
        logger.debug("birthday entries filled hit")
        logger.debug("return {}".format(rv))
        return rv

    def _create_separater_label(self):
        label = Gtk.Label("/")
        label.get_style_context().add_class("birthday_separater")
        return label

    def get_birthday_data(self):
        bday_entries = [self._day_entry, self._month_entry, self._year_entry]
        bday = []

        for entry in bday_entries:
            is_valid_number, text = self._check_entry_is_number(entry)
            if not is_valid_number:
                return (False, {})
            else:
                bday.append(text)

        return (True, {'day': bday[0], 'month': bday[1], 'year': bday[2]})

    def calculate_age(self):
        # Error messages
        default_error = N_("Oops!")
        default_desc = N_("You haven't entered a valid birthday")
        entry_not_valid = N_("You haven't entered a valid number")

        try:
            # boolean, dictionary
            valid_bday, bday = self.get_birthday_data()
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

            if current_month < bday['month']:
                age = age - 1
            elif current_month == bday['month']:
                if current_day < bday['day']:
                    age = age - 1
                # TODO: if it's their birthday, do something special?
                # elif current_day == bday_day:
                #    print "IT'S YOUR BIIIIRTHDAY"

            if age < 0 or age > 114:
                raise Exception(default_error, default_desc)

            return age, bday_date, ()

        except Exception as e:

            if len(e.args) == 1:
                error1 = default_error
                error2 = N_("There's a problem - {0}").format(e)
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
