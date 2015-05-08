#!/usr/bin/env python

# RegistrationScreen2.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.heading import Heading
from kano_registration_gui.GetData import GetData2
from kano_avatar_gui.ImageView import ImageView
from kano_avatar.paths import AVATAR_DEFAULT_LOC, AVATAR_ENV_SHIFTED
from kano_registration_gui.RegistrationScreen3 import RegistrationScreen3
from kano.logging import logger


# Get username, password and birthday data from user.
class RegistrationScreen2(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        logger.debug("setting main widget")
        self.win.set_main_widget(self)

        self.page_control = self.win.create_page_control(2, "BACK", "NEXT")
        self.page_control.next_button.set_sensitive(False)
        self.pack_end(self.page_control, False, False, 0)
        self.page_control.connect("next-button-clicked", self.next_page)
        self.page_control.connect("back-button-clicked", self.prev_page)

        title = Heading(
            'Character creator',
            'Choose a cool name and secure password'
        )

        self.pack_start(title.container, False, False, 0)

        # This time we need the picture with the login screen to one side.
        image_viewer = ImageView(self)
        self.pack_start(image_viewer, False, False, 0)

        filename = os.path.join(AVATAR_DEFAULT_LOC, AVATAR_ENV_SHIFTED)
        image_viewer.set_image(filename)
        self.data_screen = GetData2()
        self.data_screen.connect("widgets-filled", self.enable_next)
        self.data_screen.connect("widgets-empty", self.disable_next)

        # Put it with the same y-coordinate as the menu
        image_viewer.put(self.data_screen, 400, 30)
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
        RegistrationScreen3(self.win, age)

    def prev_page(self, widget):
        self.win.remove_main_widget()

        from kano_registration_gui.RegistrationScreen1 import RegistrationScreen1
        RegistrationScreen1(self.win)

    def enable_next(self, widget):
        self.page_control.enable_next()

    def disable_next(self, widget):
        self.page_control.disable_next()
