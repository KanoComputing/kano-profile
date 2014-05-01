#!/usr/bin/env python

# birthday.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set nickname of user

from gi.repository import Gtk

from components import heading, green_button
from kano_login import account_email
import time

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

        title = heading.Heading("Birthday", "So we know when to send you cake!")

        self.next_button = green_button.Button("NEXT")
        self.next_button.button.connect("button_press_event", self.set_birthday)
        self.next_button.button.set_sensitive(False)

        self.halign = Gtk.Alignment(xscale=1, yscale=1, xalign=0.5, yalign=0.5)
        self.halign.set_padding(0, 0, 60, 0)
        self.halign.add(self.entry_container)

        self.box.pack_start(title.container, False, False, 0)
        self.box.pack_start(self.halign, False, False, 30)
        self.box.pack_start(self.next_button.box, False, False, 0)

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
        print "key released"
        if self.day_entry.get_text() != "" and self.month_entry.get_text() != "" and self.year_entry.get_text() != "":
            print "button is sensitive"
            self.next_button.button.set_sensitive(True)
        else:
            print "button is not sensitive"
            self.next_button.button.set_sensitive(False)

    def set_birthday(self, arg1=None, arg2=None):
        print "setting birthday"
        age = self.calculate_age()
        if age == -1:
            return
        self.win.age = age
        account_email.activate(self.win, self.box)
        self.win.state = self.win.state + 1

    def calculate_age(self):
        try:
            bday_day = int(self.day_entry.get_text())
            bday_month = int(self.month_entry.get_text())
            bday_year = int(self.year_entry.get_text())

        except:
            dialog = Gtk.MessageDialog(self.win, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.OK, "Houston, we have a problem")
            dialog.format_secondary_text("You've not entered a valid birthday!!!!")
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                dialog.destroy()
            else:
                dialog.destroy()
            return -1

        # Get current date
        current_day = int(time.strftime("%d"))
        current_month = int(time.strftime("%m"))
        current_year = int(time.strftime("%Y"))

        age = current_year - bday_year

        if current_month < bday_month:
            age = age - 1
        elif current_month == bday_month:
            if current_day < bday_day:
                age = age - 1
            elif current_day == bday_day:
                print "IT'S YOUR BIIIIRTHDAY"

        return age


def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    win.clear_box()

    birthday = Birthday(win, box)


