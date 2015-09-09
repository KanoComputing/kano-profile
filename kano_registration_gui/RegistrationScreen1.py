#!/usr/bin/env python

# RegistrationScreen1.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from gi.repository import Gtk
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.heading import Heading
from kano_registration_gui.GetData import GetData2
from kano_registration_gui.RegistrationScreen2 import RegistrationScreen2


# Get username, password and birthday data from user.
class RegistrationScreen1(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_main_widget(self)

        self.page_control = self.win.create_page_control(1, "", _("NEXT"))
        self.page_control.next_button.set_sensitive(False)
        self.pack_end(self.page_control, False, False, 0)
        self.page_control.connect("next-button-clicked", self.next_page)

        title = Heading(
            _('Character creator'),
            _('Choose a cool name and secure password')
        )

        self.pack_start(title.container, False, False, 0)
        self.data_screen = GetData2()
        self.data_screen.connect("widgets-filled", self.enable_next)
        self.data_screen.connect("widgets-empty", self.disable_next)

        self.add(self.data_screen)
        self.win.show_all()

    def _show_error_dialog(self, title, description):
        kdialog = KanoDialog(title, description,
                             parent_window=self.win)
        kdialog.run()

    def next_page(self, widget):
        age, bday_date, error = self.data_screen.calculate_age()

        if age == -1:
            self._show_error_dialog(error[0], error[1])
            return

        # Get the username, password and birthday
        data = self.data_screen.get_entry_data()
        self.win.data = data

        # We can save the username and birthday to kano-profile
        # Don't save password as this is private
        self.data_screen.save_username_and_birthday()

        self.win.remove_main_widget()

        # Pass the age to the third registration screen so we can show the
        # appropriate number of entries available
        RegistrationScreen2(self.win, age)

    def enable_next(self, widget):
        self.page_control.enable_next()

    def disable_next(self, widget):
        self.page_control.disable_next()
