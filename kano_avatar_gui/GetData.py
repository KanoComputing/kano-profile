#!/usr/bin/env python

# GetData.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import re
from gi.repository import Gtk, GObject
from kano.gtk3.buttons import OrangeButton
from kano.gtk3.apply_styles import apply_styling_to_screen


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


class DataTemplate(Gtk.EventBox):
    __gsignals__ = {
        'entries-filled': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'entry-empty': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.width = 250
        self.height = 400
        self.set_size_request(self.width, self.height)

        CSS_PATH = "/home/kano/kano-profile/media/CSS/avatar_generator.css"
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
        self.email_entry.connect('key-release-event', self.entries_full)

        self.guardian_email_entry = LabelledEntry("Guardian's Email (optional)")
        self.guardian_email_entry.connect('key-release-event', self.entries_full)

        birthday_widget = self._create_birthday_widget()

        self.entries = [
            self.email_entry,
            self._day_entry,
            self._month_entry,
            self._year_entry
        ]

        box.pack_start(self.email_entry, False, False, 10)
        box.pack_start(self.guardian_email_entry, False, False, 10)
        box.pack_start(birthday_widget, False, False, 10)

        box.set_margin_top(20)

        self.add(box)

    def _create_birthday_widget(self):
        self._day_entry = Gtk.Entry()
        self._day_entry.set_size_request(50, -1)
        self._day_entry.set_width_chars(2)
        self._day_entry.set_placeholder_text("DD")
        self._day_entry.connect('key-release-event', self.entries_full)

        self._month_entry = Gtk.Entry()
        self._month_entry.set_size_request(50, -1)
        self._month_entry.set_width_chars(2)
        self._month_entry.set_placeholder_text("MM")
        self._month_entry.connect('key-release-event', self.entries_full)

        self._year_entry = Gtk.Entry()
        self._year_entry.set_size_request(70, -1)
        self._year_entry.set_width_chars(4)
        self._year_entry.set_placeholder_text("YYYY")
        self._year_entry.connect('key-release-event', self.entries_full)

        hbox = Gtk.Box()
        hbox.pack_start(self._day_entry, False, False, 0)
        hbox.pack_start(self._month_entry, False, False, 20)
        hbox.pack_start(self._year_entry, False, False, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        birthday_label = Gtk.Label("Birthday", xalign=0)
        birthday_label.get_style_context().add_class("get_data_label")
        vbox.pack_start(birthday_label, False, False, 0)
        vbox.pack_start(hbox, False, False, 10)
        vbox.set_size_request(0, 0)

        vbox.set_margin_left(30)

        return vbox

    def _get_birthday_data(self):
        day_text = self._day_entry.get_text()
        month_text = self._month_entry.get_text()
        year_text = self._year_entry.get_text()

        return {'day': day_text, 'month': month_text, 'year': year_text}

    def get_data(self):
        data = {}

        data['email'] = self.email_entry.get_text()
        data['guardian_email'] = self.guardian_email_entry.get_text()

        bday_data = self._get_birthday_data()
        data.update(bday_data)

        return data

    def entries_full(self, widget, event):
        full = True

        for entry in self.entries:
            text = entry.get_text()
            if not text:
                full = False
            elif entry == self.email_entry:
                full = is_email(text)

        if full:
            self.emit('entries-filled')
        else:
            self.emit('entry-empty')


class GetData3(DataTemplate):
    '''This second class registration box is to get the email,
    optional guardian's email and show the terms and conditions.
    '''

    def __init__(self):
        DataTemplate.__init__(self)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.username_entry = LabelledEntry("Username")
        self.username_entry.connect('key-release-event', self.entries_full)

        self.password_entry = LabelledEntry("Password - min. 6 letters")
        self.password_entry.connect('key-release-event', self.entries_full)
        self.password_entry.set_visibility(False)

        self.entries = [
            self.username_entry,
            self.password_entry
        ]

        # Terms and conditions check button
        self.checkbutton = Gtk.CheckButton()
        self.checkbutton.get_style_context().add_class("get_data_checkbutton")
        self.checkbutton.set_size_request(50, 50)
        self.checkbutton.connect('toggled', self.entries_full)
        self.checkbutton.set_margin_left(30)

        tc_button = OrangeButton("I agree to the terms and conditions")
        tc_button.connect("clicked", self.launch_t_and_cs)
        hbox = Gtk.Box()
        hbox.pack_start(self.checkbutton, False, False, 0)
        hbox.pack_start(tc_button, False, False, 0)

        box.pack_start(self.username_entry, False, False, 10)
        box.pack_start(self.password_entry, False, False, 10)
        box.pack_start(hbox, False, False, 10)

        box.set_margin_top(20)

        self.add(box)

    def launch_t_and_cs(self, widget):
        # TODO: find out how to launch this.  Dialog?
        print "launch terms and conditions"

    def get_data(self):
        data = {}

        data['username'] = self.username_entry.get_text()
        data['password'] = self.password_entry.get_text()

        return data

    def entries_full(self, widget=None, event=None):
        full = True

        for entry in self.entries:
            if not entry.get_text():
                full = False

        checked = self.checkbutton.get_active()

        if checked and full:
            self.emit('entries-filled')
        else:
            self.emit('entry-empty')


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
