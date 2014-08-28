#!/usr/bin/env python

# about_you.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set age and gender of user

import time
import datetime
from gi.repository import Gtk, Gdk

from kano.utils import is_number
from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.kano_combobox import KanoComboBox
from kano.gtk3.labelled_entries import add_heading

from kano_login.templates.top_bar_template import TopBarTemplate
from kano_login.register import Register
from kano_login.data import get_data


months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


class AboutYou(TopBarTemplate):
    data = get_data("ABOUT_YOU")

    # add argument to say which screen we came from - Login or FirstScreen
    def __init__(self, win, prev_screen):

        TopBarTemplate.__init__(self, "About You", prev_screen)

        self.win = win
        self.win.set_main_widget(self)
        self.enable_prev()

        title = Heading("About you", "")

        self.entry = Gtk.Entry()

        self.create_gender_widget()
        self.create_birthday_widget()

        self.next_button = KanoButton("NEXT")
        self.next_button.pack_and_align()
        self.next_button.connect("button_release_event", self.save_info)
        self.next_button.connect("key_release_event", self.save_info)

        self.box.pack_start(title.container, False, False, 3)
        self.box.pack_start(self.gender_widget, False, False, 10)
        self.box.pack_start(self.birthday_widget, False, False, 10)
        self.box.pack_start(self.next_button.align, False, False, 20)

        self.win.show_all()

    def repack(self):
        self.win.clear_win()
        self.win.set_main_widget(self)

    def create_gender_widget(self):
        self.boy_widget = Gtk.RadioButton.new_with_label(None, "Boy")
        self.boy_widget.connect("toggled", self.get_gender)
        self.girl_widget = Gtk.RadioButton.new_with_label_from_widget(self.boy_widget, "Girl")
        self.girl_widget.connect("toggled", self.get_gender)
        self.wizard_widget = Gtk.RadioButton.new_with_label_from_widget(self.boy_widget, "Wizard")
        self.wizard_widget.connect("toggled", self.get_gender)

        self.selected_gender = "Boy"

        box = Gtk.Box(spacing=20)
        box.pack_start(self.boy_widget, False, False, 0)
        box.pack_start(self.girl_widget, False, False, 0)
        box.pack_start(self.wizard_widget, False, False, 0)

        new_box = add_heading("Gender", box, True)

        self.gender_widget = new_box
        self.gender_widget.set_margin_left(15)

    def create_birthday_widget(self):
        box = Gtk.Box(spacing=20)

        self.day_widget = KanoComboBox(max_display_items=7)
        for i in range(1, 32):
            self.day_widget.append(str(i))
        self.day_widget.set_selected_item_index(0)

        self.month_widget = KanoComboBox(max_display_items=7)
        for month in months:
            self.month_widget.append(month)
        self.month_widget.set_selected_item_index(0)

        self.year_widget = Gtk.Entry()
        self.year_widget.set_placeholder_text("XXXX")
        self.year_widget.set_width_chars(4)
        self.year_widget.set_max_length(4)
        self.year_widget.set_size_request(45, 47)

        labelled_day = add_heading("DAY", self.day_widget)
        labelled_month = add_heading("MONTH", self.month_widget)
        labelled_year = add_heading("YEAR", self.year_widget)

        year_align = Gtk.Alignment()
        year_align.set_padding(2, 0, 0, 0)
        year_align.add(labelled_year)

        box.pack_start(labelled_day, False, False, 0)
        box.pack_start(labelled_month, False, False, 0)
        box.pack_start(year_align, False, False, 0)

        new_box = add_heading("Birthday", box, True)

        self.birthday_widget = new_box
        self.birthday_widget.set_margin_left(15)

    def save_info(self, widget, event, args=[]):
        if not hasattr(event, 'keyval') or Gdk.keyval_name(event.keyval) == "Return":

            age, bday_date = self.calculate_age()

            if age == -1:
                return

            # Save age and birthday as part of the window object
            self.win.age = age
            self.win.bday_date = bday_date

            gender = self.selected_gender
            self.win.gender = gender
            self.win.clear_win()

            if age < 13:
                Register(self.win, self, False)

            else:
                Register(self.win, self, True)

    def get_gender(self, widget):
        if widget.get_active():
            label = widget.get_label()
            self.selected_gender = label

    def calculate_age(self):
        try:
            year_text = self.year_widget.get_text()
            if not is_number(year_text):
                raise Exception(self.data["ALERT_TITLE_NO_YEAR"], self.data["ALERT_DESCRIPTION_NO_YEAR"])

            bday_day = int(self.day_widget.get_selected_item_text())
            month_str = self.month_widget.get_selected_item_text()
            bday_month = months.index(month_str) + 1
            bday_year = int(self.year_widget.get_text())
            self.win.date_split = (bday_year, bday_month, bday_day)

            bday_date = str(datetime.date(bday_year, bday_month, bday_day))

            # To allow people to enter their year as a two digit number
            if bday_year < 15 and bday_year >= 0:
                bday_year = bday_year + 2000
            elif bday_year >= 15 and bday_year <= 99:
                bday_year = bday_year + 1900

            # Get current date
            current_day = int(time.strftime("%d"))
            current_month = int(time.strftime("%m"))
            current_year = int(time.strftime("%Y"))

            age = current_year - bday_year
            if age < 0:
                raise Exception(self.data["ALERT_TITLE_DEFAULT"], self.data["ALERT_DESCRIPTION_DEFAULT"])
            elif age > 114:
                raise Exception(self.data["ALERT_TITLE_DEFAULT"], self.data["ALERT_DESCRIPTION_DEFAULT"])

            if current_month < bday_month:
                age = age - 1
            elif current_month == bday_month:
                if current_day < bday_day:
                    age = age - 1
                # TODO: if it's their birthday, do something special?
                # elif current_day == bday_day:
                #    print "IT'S YOUR BIIIIRTHDAY"
            return age, bday_date

        except Exception as e:
            kdialog = None
            if len(e.args) == 1:
                kdialog = KanoDialog(self.data["ALERT_TITLE_DEFAULT"],
                                     "There's a problem - {0}".format(e),
                                     parent_window=self.win)
            elif len(e.args) == 2:
                kdialog = KanoDialog(e[0], e[1],
                                     parent_window=self.win)
            else:
                kdialog = KanoDialog(self.data["ALERT_TITLE_DEFAULT"],
                                     self.data["ALERT_DESCRIPTION_DEFAULT"],
                                     parent_window=self.win)
            kdialog.run()
            return -1, -1
