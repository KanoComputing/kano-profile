#!/usr/bin/env python

# RegistrationScreen1.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import subprocess

from gi.repository import Gtk, Gdk

from kano.gtk3.buttons import KanoButton
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.heading import Heading
from kano.network import is_internet
from kano.logging import logger
from kano_world.functions import request_wrapper, content_type_json
from kano_world.functions import register as register_
from kano_profile.tracker import track_data, \
    save_hardware_info, save_kano_version
from kano.utils import run_bg

from kano_registration_gui.GetData import GetData1
from kano_profile.paths import bin_dir


# Get username, password and birthday data from user.
class RegistrationScreen1(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_main_widget(self)
        self.win.set_decorated(True)

        # self.page_control = self.win.create_page_control(1, "", _("NEXT"))
        # self.page_control.next_button.set_sensitive(False)
        # self.pack_end(self.page_control, False, False, 0)
        # self.page_control.connect("next-button-clicked", self.next_page)
        self._register_button = KanoButton(_("Join Kano World").upper())
        self._register_button.set_sensitive(False)
        self._register_button.set_margin_top(10)
        self._register_button.set_margin_left(30)
        self._register_button.set_margin_right(30)
        self._register_button.set_margin_bottom(30)
        self._register_button.connect('clicked', self._on_register_button)
        self.pack_end(self._register_button, False, False, 0)

        title = Heading(
            _('Kano World'),
            _('Choose a cool name and secure password')
        )

        self.pack_start(title.container, False, False, 0)
        self.data_screen = GetData1()
        # self.data_screen.connect("widgets-filled", self.enable_next)
        # self.data_screen.connect("widgets-empty", self.disable_next)
        self.data_screen.connect("widgets-filled", self.enable_register_button)
        self.data_screen.connect("widgets-empty", self.disable_register_button)

        self.add(self.data_screen)
        self.win.show_all()

    def _show_error_dialog(self, title, description):
        kdialog = KanoDialog(title, description,
                             parent_window=self.win)
        kdialog.run()

    def _on_register_button(self, widget):
        # age, bday_date, error = self.data_screen.calculate_age()

        # if age == -1:
        #     self._show_error_dialog(error[0], error[1])
        #     return

        # Get the username, password and birthday
        data = self.data_screen.get_widget_data()
        username = data["username"]

        if not self.is_username_available(username):
            track_data('world-registration-username-taken',
                       {'username': username})
            kd = KanoDialog(
                "This username is taken!",
                "Try another one",
                parent_window=self.win
            )
            kd.run()
            self.data_screen.username.set_text("")
            self.data_screen.validate_username()
            self.data_screen.username.grab_focus()
            return

        # self.win.data = data

        # We can save the username and birthday to kano-profile
        # Don't save password as this is private
        self.data_screen.save_username_and_birthday()

        # self.win.remove_main_widget()

        # Pass the age to the third registration screen so we can show the
        # appropriate number of entries available
        # RegistrationScreen2(self.win, age)
        self.register_user_with_gui()

    def enable_register_button(self, widget):
        self._register_button.set_sensitive(True)

    def disable_register_button(self, widget):
        self._register_button.set_sensitive(False)

    def is_username_available(self, name):
        '''
        Returns True if username is available, and False otherwise
        '''
        # Use the endpoint api.kano.me/users/username/:name
        success, text, data = request_wrapper(
            'get',
            '/users/username/{}'.format(name),
            headers=content_type_json
        )

        if not success and text.strip() == "User not found":
            return True
        elif success:
            # Username is definitely taken
            return False
        else:
            # Maybe let the user know something went wrong? e.g. if there's no
            # internet, launch a dialog at this point
            return False

    def register_user_with_gui(self):
        self.data_screen.cache_emails()
        data = self.data_screen.get_widget_data()
        # self.data_screen.cache_marketing_choice()

        # self.page_control.disable_buttons()
        # self.data_screen.disable_all()
        # self.get_email_data()

        # Make cursor into a spinner
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.win.get_window().set_cursor(watch_cursor)

        # This means no threads are needed.
        while Gtk.events_pending():
            Gtk.main_iteration()

        # Try and register the account on the server
        email = data["email"]
        # secondary_email = self.win.data["secondary_email"]
        username = data["username"]
        password = data["password"]
        # date_year = self.win.data["year"]
        # date_month = self.win.data["month"]
        # date_day = self.win.data["day"]
        marketing_enabled = True

        success, text = register_(email, username, password,
                                  marketing_enabled=marketing_enabled)

        # This should no longer be needed, since this is checked in the first screen.
        # However there is a small chance someone could take the username
        # while the user is in the process of registering
        if not success:
            if text.strip() == "Cannot register, problem: Username already registered":

                logger.info('username invalid - getting second username')
                self.collect_new_username()
                return

            else:
                logger.info('problem with registration: {}'.format(text))
                return_value = "FAIL"
                self.create_dialog(
                    title=_("Houston, we have a problem"),
                    description=str(text)
                )
                track_data('world-registration-failed', {'reason': text})

        else:
            logger.info('registration successful')

            # bday_date = str(datetime.date(date_year, date_month, date_day))
            # save_profile_variable(
            #     'birthdate',
            #     bday_date,
            #     skip_kdesk_refresh=True
            # )

            # saving hardware info and initial Kano version
            save_hardware_info()
            save_kano_version()

            # running kano-sync after registration
            logger.info('running kano-sync after successful registration')
            cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            run_bg(cmd)

            return_value = "SUCCEED"
            self.create_dialog(
                title=_("Profile activated!"),
                description=_("Now you can share stuff, build your character, "
                              "and connect with friends.")
            )

        # self.page_control.enable_buttons()
        # self.data_screen.enable_all()
        self.win.get_window().set_cursor(None)

        # Close the app if it was successful
        if return_value == "SUCCEED":
            Gtk.main_quit()

    def _check_for_internet(self):
        if not is_internet():
            kd = KanoDialog(
                "You don't have internet",
                "Do you want to connect to WiFi?",
                [
                    {
                        "label": "YES",
                        "color": "green",
                        "return_value": 0
                    },
                    {
                        "label": "NO",
                        "color": "red",
                        "return_value": 1
                    }
                ],
                parent_window=self.win
            )
            response = kd.run()

            # Close the dialog
            while Gtk.events_pending():
                Gtk.main_iteration()

            if response == 0:
                subprocess.Popen("sudo kano-wifi-gui", shell=True)

            return

    def create_dialog(self, title, description):
        kdialog = KanoDialog(
            title,
            description,
            parent_window=self.win
        )
        rv = kdialog.run()
        return rv
