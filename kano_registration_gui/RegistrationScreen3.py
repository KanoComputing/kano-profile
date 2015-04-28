#!/usr/bin/env python

# RegistrationScreen3.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import datetime
from gi.repository import Gtk, Gdk

from kano_avatar_gui.ImageView import ImageView
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog
from kano_registration_gui.GetData import GetData3, cache_data, get_cached_data
from kano_world.functions import register as register_
from kano_profile.profile import save_profile_variable
from kano_profile.tracker import save_hardware_info, save_kano_version
from kano_profile.paths import bin_dir
from kano.network import is_internet
from kano.logging import logger
from kano.utils import run_bg


# Get emails and show the terms and conditions
class RegistrationScreen3(Gtk.Box):

    def __init__(self, win, age):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_main_widget(self)

        self.page_control = self.win.create_page_control(3, "BACK", "CONTINUE")
        self.page_control.disable_next()
        self.pack_end(self.page_control, False, False, 0)
        self.page_control.connect("next-button-clicked", self.register_handler)
        self.page_control.connect("back-button-clicked", self.prev_page)

        title = Heading('Character creator', 'Sign up with your email')
        self.pack_start(title.container, False, False, 0)

        image_viewer = ImageView(self)
        self.pack_start(image_viewer, False, False, 0)

        # Get character image
        filename = os.path.join(os.path.expanduser('~'),
                                "avatar-content/avatar_inc_env_page2.png")
        image_viewer.set_image(filename)

        # Pass age into the Data screen - decide whether to ask for
        # Guardian's email
        self.data_screen = GetData3(age)
        self.data_screen.connect("widgets-filled", self.enable_next)
        self.data_screen.connect("widgets-empty", self.disable_next)

        # Put it with the same y coordinate as the menu
        image_viewer.put(self.data_screen, 400, 30)

        self.show_all()

    def prev_page(self, widget):
        from kano_registration_gui.RegistrationScreen2 import RegistrationScreen2

        self.data_screen.cache_emails()
        self.win.remove_main_widget()
        page = RegistrationScreen2(self.win)
        self.win.set_main_widget(page)

    def enable_next(self, widget):
        self.page_control.enable_next()

    def disable_next(self, widget):
        self.page_control.disable_next()

    def get_email_data(self):
        # Add the info about the emails to the self.win.data parameter
        self.win.data.update(self.data_screen.get_email_entry_data())

    def register_handler(self, widget=None, arg=None):

        if not is_internet():
            # this will launch dialogs until either the user
            # connects to internet or quits
            self.try_to_connect_to_internet()

        if is_internet():
            self.register_user_with_gui()
        else:
            Gtk.main_quit()

    def register_user_with_gui(self):
        self.data_screen.cache_emails()
        self.page_control.disable_buttons()
        self.data_screen.disable_all()
        self.get_email_data()

        # Make cursor into a spinner
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.win.get_window().set_cursor(watch_cursor)

        # This means no threads are needed.
        while Gtk.events_pending():
            Gtk.main_iteration()

        # Try and register the account on the server
        email = self.win.data["email"]
        secondary_email = self.win.data["secondary_email"]
        username = self.win.data["username"]
        password = self.win.data["password"]
        date_year = self.win.data["year"]
        date_month = self.win.data["month"]
        date_day = self.win.data["day"]

        logger.info('trying to register user with data {} {} {} {} {} {} {}'
                    .format(
                        email, secondary_email, username, password, date_year,
                        date_month, date_day
                    )
                    )

        success, text = register_(email, username, password,
                                  date_year, date_month, date_day,
                                  secondary_email=secondary_email)

        if not success:
            if text.strip() == "Cannot register, problem: Username already registered":

                logger.info('username invalid - getting second username')
                self.collect_new_username()
                return

            else:
                logger.info('problem with registration: {}'.format(text))
                title = "Houston, we have a problem"
                description = str(text)
                return_value = "FAIL"
                self.create_dialog(title, description)

        else:
            logger.info('registration successful')

            bday_date = str(datetime.date(date_year, date_month, date_day))
            save_profile_variable('birthdate', bday_date)

            # saving hardware info and initial Kano version
            save_hardware_info()
            save_kano_version()

            # running kano-sync after registration
            logger.info('running kano-sync after successful registration')
            cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            run_bg(cmd)

            title = "Profile created!"
            description = ("Now you can share stuff, build your character, "
                           "and connect with friends.")
            return_value = "SUCCEED"
            self.create_dialog(title, description)

        self.page_control.enable_buttons()
        self.data_screen.enable_all()
        self.win.get_window().set_cursor(None)

        # Close the app if it was successful
        if return_value == "SUCCEED":
            Gtk.main_quit()

    def create_dialog(self, title, description):
        kdialog = KanoDialog(
            title,
            description,
            parent_window=self.win
        )
        rv = kdialog.run()
        return rv

    def collect_new_username(self):
        username_entry = Gtk.Entry()
        title = "Oops, that username has already been taken!"
        description = "Try picking another one."

        kdialog = KanoDialog(
            title,
            description,
            button_dict=[
                {
                    "label": "OK"
                },
                {
                    "label": "GO BACK TO WINDOW",
                    "return_value": "CANCEL",
                    "color": "red"
                }
            ],
            widget=username_entry,
            has_entry=True,
            parent_window=self.win
        )
        rv = kdialog.run()
        if rv == "CANCEL":
            # let dialog close, do nothing
            self.page_control.enable_buttons()
            self.data_screen.enable_all()
            self.win.get_window().set_cursor(None)
        else:
            # rv will be the entry contents
            self.win.data["username"] = rv

            # Store this in kano profile straight away
            cache_data("username", rv)
            self.register_handler()

    # TODO: the following could be neatened up
    ###################################################

    def try_to_connect_to_internet(self):
        title = "You don't have internet!"
        description = "Connect to WiFi and try again."
        rv = self.connect_dialog(title, description)

        # the dialog should close here
        logger.debug("dialog should close here")

        if rv == "connect":
            # launch wifi setup
            self.win.blur()
            while Gtk.events_pending():
                Gtk.main_iteration()

            logger.debug("Launching the wifi gui")
            os.system("sudo /usr/bin/kano-wifi-gui")
            logger.debug("Finished with the wifi gui")

            keep_checking = True

            if is_internet():
                keep_checking = False

            while keep_checking:
                keep_checking = self.keep_trying_to_connect()

        else:
            # exit app
            logger.debug("Killing application")
            Gtk.main_quit()

    def keep_trying_to_connect(self):
        title = "Still not connected..."
        description = (
            "Seems like you're having trouble connecting.\n"
            "Try again later at another point"
        )
        rv = self.connect_dialog(title, description)

        if rv == "connect":
            logger.debug("Second launching wifi gui")
            self.win.blur()

            while Gtk.events_pending():
                Gtk.main_iteration()

            os.system("sudo /usr/bin/kano-wifi-gui")
            logger.debug("Second finished launching wifi gui")

            if is_internet():
                return False

            return True
        else:
            # exit app
            logger.debug("Killing application")
            return False

    def connect_dialog(self, title, description):
        button_dict = [
            {
                "label": "LATER",
                "color": "red",
                "return_value": "later"
            },
            {
                "label": "CONNECT TO WIFI",
                "color": "green",
                "return_value": "connect"
            }
        ]
        kdialog = KanoDialog(title, description, button_dict,
                             parent_window=self.win)
        rv = kdialog.run()
        return rv
