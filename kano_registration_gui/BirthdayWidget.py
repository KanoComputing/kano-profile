#!/usr/bin/env python

# BirthdayWidget.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, GObject
import time
import datetime
import calendar

from kano.logging import logger
from kano.gtk3.kano_combobox import KanoComboBox


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
        KanoComboBox.apply_styling_to_screen()

        current_year = datetime.datetime.now().year
        years = [str(i) for i in range(current_year, 1900, -1)]
        self._year_dropdown = self._create_dropdown(years, "Year")
        self._year_dropdown.connect("changed", self._update_day_dropdown)

        months = []
        for i in range(1, 13):
            months.append(calendar.month_name[i])

        self._month_dropdown = self._create_dropdown(months, "Month", width=60)
        self._month_dropdown.connect("changed", self._update_day_dropdown)

        # When the month gets changed, the day gets changed.
        # At start, shows days 1-31
        days = [str(i) for i in range(1, 32)]
        self._day_dropdown = self._create_dropdown(days, "Day")

        hbox = Gtk.Box()
        hbox.pack_start(self._year_dropdown, False, False, 10)
        hbox.pack_start(self._month_dropdown, False, False, 10)
        hbox.pack_start(self._day_dropdown, False, False, 10)
        hbox.set_margin_left(20)
        hbox.set_margin_right(10)

        # validation
        label_box = Gtk.Box()
        label_box.set_margin_left(30)

        birthday_label = Gtk.Label(_("Birthday"))
        birthday_label.get_style_context().add_class("get_data_label")
        label_box.pack_start(birthday_label, False, False, 0)

        self._birthday_status = Gtk.Label()
        self._birthday_status.get_style_context().add_class("validation_label")
        label_box.pack_start(self._birthday_status, False, False, 0)

        # Container for the validation and title labels
        self.pack_start(label_box, False, False, 0)

        # Container for the dropdowns
        self.pack_start(hbox, False, False, 0)

    def _create_dropdown(self, item_list, default_text=None, width=-1):

        logger.debug("in create_dropdown, item_list = {}".format(item_list))
        if default_text:
            dropdown = KanoComboBox(default_text=default_text,
                                    max_display_items=7)
        else:
            dropdown = KanoComboBox(max_display_items=7)

        dropdown.set_size_request(width, -1)

        for i in item_list:
            dropdown.append(i)

        # TODO: check birthday is valid when selection has been made
        dropdown.connect("changed", self.validate)

        return dropdown

    def _update_day_dropdown(self, widget):
        logger.debug("changing day dropdown")

        # Get new list of days
        # First, get the selected year and selected month

        year = self._get_year()
        month = self._get_month()

        if year == 0 or month == 0:
            logger.debug("returning as year or month is blank, year = {}, month = {}".format(year, month))
            # Don't update the days
            return

        logger.debug("not returning, month = {}, year = {}".format(month, year))
        days = calendar.monthrange(year, month)[1]
        logger.debug("days dropdown changing, days = {}".format(days))

        days_list = [str(i) for i in range(1, days + 1)]
        self._day_dropdown.set_items(days_list)

    def validate(self, *dummy):
        day = self._str_to_int(self._day_dropdown.get_selected_item_text())
        month = self._month_dropdown.get_selected_item_index() + 1
        year = self._str_to_int(self._year_dropdown.get_selected_item_text())

        if self.FIELD_INCOMPLETE in [day, year] or month == 0:
            return self._set_validation_msg('', False)

        try:
            birthday = datetime.date(year, month, day)
        except Exception as e:
            logger.debug("Exception raised when validating = {}".format(str(e)))
            return

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
        bday = {}
        bday["day"] = self._get_day()
        bday["month"] = self._get_month()
        bday["year"] = self._get_year()

        return (True, bday)

    def _get_day(self):
        '''
            Returns an integer of the birthday day
        '''
        return self._str_to_int(self._day_dropdown.get_selected_item_text())

    def _get_month(self):
        '''
            Returns an integer of the birthday month
        '''
        return self._month_dropdown.get_selected_item_index() + 1

    def _get_year(self):
        '''
            Returns an integer of the birthday year
        '''
        return self._str_to_int(self._year_dropdown.get_selected_item_text())

    def calculate_age(self):
        # Error messages
        default_error = N_("Oops!")
        default_desc = N_("You haven't entered a valid birthday")
        entry_not_valid = N_("You haven't entered a valid number")

        try:
            # boolean, dictionary
            valid_bday, bday = self.get_birthday_data()
            print "birthday data {} {}".format(valid_bday, bday)

            if not valid_bday:
                raise Exception(default_error, entry_not_valid)

            logger.debug("User birthday = {}".format(bday))

            bday_date = str(datetime.date(bday["year"],
                                          bday["month"],
                                          bday["day"]))
            print "bday_date = {}".format(bday_date)

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
