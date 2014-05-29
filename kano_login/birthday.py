#!/usr/bin/env python

# birthday.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set birthday of user

from gi.repository import Gtk

import kano.gtk3.kano_dialog as kano_dialog
from kano.gtk3.green_button import GreenButton
from kano.gtk3.heading import Heading
from kano_login import register
import time
import datetime

win = None
box = None


class Birthday():
    def __init__(self, win, box):
        self.win = win
        self.box = box

        self.day_entry = self.create_entry("Day")
        self.day_box = self.create_box(self.day_entry)
        self.month_entry = self.create_entry("Month")
        self.month_box = self.create_box(self.month_entry)
        self.year_entry = self.create_entry("Year")
        self.year_box = self.create_box(self.year_entry)

        self.entry_container = Gtk.Box()
        self.entry_container.pack_start(self.day_box, False, False, 0)
        self.entry_container.pack_start(self.month_box, False, False, 20)
        self.entry_container.pack_start(self.year_box, False, False, 0)

        title = Heading("When's your birthday?", "We'll send you a code cake!")

        self.next_button = GreenButton("NEXT")
        self.next_button.pack_and_align()
        self.next_button.connect("button_press_event", self.set_birthday)
        self.next_button.connect("key_press_event", self.set_birthday)
        self.next_button.set_sensitive(False)

        self.halign = Gtk.Alignment(xscale=1, yscale=1, xalign=0.5, yalign=0.5)
        self.halign.set_padding(0, 0, 60, 0)
        self.halign.add(self.entry_container)

        self.box.pack_start(title.container, False, False, 0)
        self.box.pack_start(self.halign, False, False, 30)
        self.box.pack_start(self.next_button.align, False, False, 0)

        self.box.show_all()

    def create_entry(self, placeholder_text):
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder_text)
        entry.set_width_chars(5)
        entry.connect("key_release_event", self.update_next_button)
        return entry

    def create_box(self, widget):
        box = Gtk.Box()
        box.add(widget)
        box.set_size_request(44, 44)
        return box

    def update_next_button(self, arg1=None, arg2=None):
        if self.day_entry.get_text() != "" and self.month_entry.get_text() != "" and self.year_entry.get_text() != "":
            self.next_button.set_sensitive(True)
        else:
            self.next_button.set_sensitive(False)

    def set_birthday(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            age, date = self.calculate_age()
            if age == -1:
                return
            self.win.age = age
            self.win.date = date
            win.update()
            register.activate(self.win, self.box)

    def calculate_age(self):
        try:
            bday_day = int(self.day_entry.get_text())
            bday_month = int(self.month_entry.get_text())
            bday_year = int(self.year_entry.get_text())
            bday_date = str(datetime.date(bday_year, bday_month, bday_day))

            # Get current date
            current_day = int(time.strftime("%d"))
            current_month = int(time.strftime("%m"))
            current_year = int(time.strftime("%Y"))

            age = current_year - bday_year
            if age < 0:
                raise Exception("Hmmm, really?", "Apparently you haven't been born yet...")
            elif age > 114:
                raise Exception("Well done for living this long!", "(But I don't believe you)")

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
                kdialog = kano_dialog.KanoDialog(e.args[0], e.args[1])
            else:
                kdialog = kano_dialog.KanoDialog("Houston, we have a problem", "You've not entered a valid birthday!")
            kdialog.run()
            self.day_entry.set_text("")
            self.month_entry.set_text("")
            self.year_entry.set_text("")
            self.next_button.set_sensitive(False)
            return -1, -1


def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    win.clear_box()

    birthday = Birthday(win, box)
