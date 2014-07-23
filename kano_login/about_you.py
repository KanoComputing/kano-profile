#!/usr/bin/env python

# about_you.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set age and gender of user

import time
import datetime
from gi.repository import Gtk

from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog

from kano_login.templates.top_bar_template import TopBarTemplate
from kano_login.misc import add_heading
from kano_login.register import Register
from kano_login.data import get_data


months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


class AboutYou(TopBarTemplate):
    data = get_data("ABOUT_YOU")

    # add argument to say which screen we came from - Login or FirstScreen
    def __init__(self, win):

        TopBarTemplate.__init__(self, "About You")

        self.win = win
        self.win.add(self)

        title = Heading("About you", "")

        self.entry = Gtk.Entry()

        self.create_gender_widget()
        self.create_birthday_widget()

        self.next_button = KanoButton("NEXT")
        self.next_button.pack_and_align()
        self.next_button.connect("button_release_event", self.save_info)
        self.next_button.connect("key_press_event", self.save_info)

        self.box.pack_start(title.container, False, False, 3)
        self.box.pack_start(self.gender_widget, False, False, 10)
        self.box.pack_start(self.birthday_widget, False, False, 10)
        self.box.pack_start(self.next_button.align, False, False, 20)

        self.win.show_all()

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

    def create_birthday_widget(self):
        box = Gtk.Box(spacing=20)

        self.day_widget = Gtk.ComboBoxText()
        for i in range(1, 32):
            self.day_widget.append_text(str(i))
        self.day_widget.set_active(0)

        self.month_widget = Gtk.ComboBoxText()

        for month in months:
            self.month_widget.append_text(month)
        self.month_widget.set_active(0)

        self.year_widget = Gtk.Entry()
        self.year_widget.set_placeholder_text("1990")
        self.year_widget.set_width_chars(4)
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

    def save_info(self, widget, event, args=[]):
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
            Register(self.win, False)

        else:
            Register(self.win, True)

    def get_gender(self, widget):
        if widget.get_active():
            label = widget.get_label()
            self.selected_gender = label

    def calculate_age(self):
        try:
            bday_day = int(self.day_widget.get_active_text())
            month_str = self.month_widget.get_active_text()
            bday_month = months.index(month_str) + 1
            bday_year = int(self.year_widget.get_text())

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
                #elif current_day == bday_day:
                #    print "IT'S YOUR BIIIIRTHDAY"
            return age, bday_date

        except Exception as e:
            kdialog = None
            if len(e.args) > 1:
                kdialog = KanoDialog(e.args[0], e.args[1])
            else:
                kdialog = KanoDialog(self.data["ALERT_TITLE_DEFAULT"], self.data["ALERT_DESCRIPTION_DEFAULT"])
            kdialog.run()
            return -1, -1
