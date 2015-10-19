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
        self._day_dropdown.connect("changed", self.validate)

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

        if default_text:
            dropdown = KanoComboBox(default_text=default_text,
                                    max_display_items=7)
        else:
            dropdown = KanoComboBox(max_display_items=7)

        dropdown.set_size_request(width, -1)

        for i in item_list:
            dropdown.append(i)

        return dropdown

    def _update_day_dropdown(self, widget):
        logger.debug("changing day dropdown")

        # Day dropdown is empty, so remove any validation message
        self._set_validation_msg("", False)

        # Get new list of days
        # First, get the selected year and selected month

        year = self._get_year()
        month = self._get_month()

        if year == 0 or month == 0:
            logger.debug("returning as year or month is blank, year = {}, month = {}".format(year, month))
            # Update the days as an empty list
            self._day_dropdown.remove_all()
            self._day_dropdown.set_text("Day")
            return

        logger.debug("not returning, month = {}, year = {}".format(month, year))
        days = calendar.monthrange(year, month)[1]
        logger.debug("days dropdown changing, days = {}".format(days))

        days_list = [str(i) for i in range(1, days + 1)]
        self._day_dropdown.set_items(days_list)

        # Unselect the current item
        self._day_dropdown.selected_item_index = -1
        self._day_dropdown.selected_item_text = ""
        self._day_dropdown.set_text("Day")

    def validate(self, *dummy):
        day = self._str_to_int(self._day_dropdown.get_selected_item_text())
        month = self._month_dropdown.get_selected_item_index() + 1
        year = self._str_to_int(self._year_dropdown.get_selected_item_text())

        logger.debug("validate function")
        logger.debug("day = {}".format(day))
        logger.debug("month = {}".format(month))
        logger.debug("year = {}".format(year))

        if self.FIELD_INCOMPLETE in [day, year] or month == 0:
            return self._set_validation_msg('', False)

        try:
            birthday = datetime.date(year, month, day)
        except Exception as e:
            logger.debug("Exception raised when validating = {}".format(str(e)))
            return

        today = datetime.date.today()
        if birthday > today:
            return self._set_validation_msg(_(' date is in the future'), False)

        oldest_date = today.replace(year=(today.year - 100))
        if birthday < oldest_date and (birthday.year < 0 or birthday.year > 99):
            return self._set_validation_msg(_(' year out of range'), False)

        return self._set_validation_msg(_(' is valid'), True)

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

    def get_birthday_data(self):
        bday = {}
        bday["day"] = self._get_day()
        bday["month"] = self._get_month()
        bday["year"] = self._get_year()
        bday["day_index"] = self._get_day_index()
        bday["month_index"] = self._get_month_index()
        bday["year_index"] = self._get_year_index()

        return bday

    def set_birthday_data(self, year_index, month_index, day_index):
        # Get the data from the cache
        # Can set value from the index, so either find the index in the
        # combobox or store it
        if year_index is not None:
            self._year_dropdown.set_selected_item_index(year_index)
        if month_index is not None:
            self._month_dropdown.set_selected_item_index(month_index)
        if day_index is not None:
            self._day_dropdown.set_selected_item_index(day_index)

        self.validate()

    def _get_day(self):
        '''
            Returns an integer of the birthday day
            If the return value is 0, then nothing has been selected
        '''
        return self._str_to_int(self._day_dropdown.get_selected_item_text())

    def _get_day_index(self):
        return self._day_dropdown.get_selected_item_index()

    def _get_month(self):
        '''
            Returns an integer of the birthday month
            If the return value is 0, then nothing has been selected
        '''
        return self._month_dropdown.get_selected_item_index() + 1

    def _get_month_index(self):
        return self._month_dropdown.get_selected_item_index()

    def _get_year(self):
        '''
            Returns an integer of the birthday year
            If the return value is 0, then nothing has been selected
        '''
        return self._str_to_int(self._year_dropdown.get_selected_item_text())

    def _get_year_index(self):
        return self._year_dropdown.get_selected_item_index()

    def calculate_age(self):
        # Error messages
        default_error = N_("Oops!")
        default_desc = N_("You haven't entered a valid birthday")
        # entry_not_valid = N_("You haven't entered a valid number")

        try:
            # boolean, dictionary
            bday = self.get_birthday_data()
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
