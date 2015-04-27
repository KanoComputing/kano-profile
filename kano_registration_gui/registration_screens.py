#!/usr/bin/env python

# registration_screens.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import threading
import datetime
from gi.repository import Gtk, Gdk, GObject

from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog
from kano.logging import logger
from kano.network import is_internet
from kano.utils import run_bg

from kano_avatar_gui.ImageView import ImageView

from kano_world.functions import register as register_
from kano_world.connection import request_wrapper

from kano_profile.tracker import save_hardware_info, save_kano_version
from kano_profile.paths import bin_dir
from kano_profile.profile import save_profile_variable

from kano_registration_gui.GetData import GetData2, GetData3


def does_user_exist(username):
    '''username is the string of the username which we want to see
    is registered.
    If return True, exists,
    If return False, does not exist
    May return None, in which case not sure?
    '''
    user_request = "/users/username/{}".format(username)
    success, text, data = request_wrapper('get', user_request)
    if success:
        return True
    elif not success and text == "User not found":
        return False

    # Could have failed because of bad internet connection, or server timed
    # out.  Inconclusive.
    return None


# Page 1 is the character personalisation
class RegistrationScreen1(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_decorated(True)
        self.win.set_main_widget(self)

        title = Heading('Make your Character',
                        'Change how the character looks')

        self.pack_start(title.container, False, False, 0)
        self.pack_start(self.win.char_creator, False, False, 0)

        # no back button on first page
        self.page_control = self.win.create_page_control(1, "", "NEXT")
        self.pack_end(self.page_control, False, False, 0)
        self.page_control.connect("next-button-clicked", self.next_page)

        self.win.show_all()

        # This hides the pop up category when using the back button
        self.win.char_creator._hide_pop_ups()

    def next_page(self, widget):
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.win.get_window().set_cursor(watch_cursor)
        self.page_control.disable_buttons()

        t = threading.Thread(target=self.save_character_and_go_next)
        t.start()

    def save_character_and_go_next(self):
        self.win.char_creator.save()

        def done():
            self.win.remove_main_widget()
            self.remove(self.win.char_creator)

            page = RegistrationScreen2(self.win)
            self.win.set_main_widget(page)

            self.win.get_window().set_cursor(None)

        GObject.idle_add(done)


# Get username, password and birthday data from user.
class RegistrationScreen2(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win

        self.page_control = self.win.create_page_control(2, "BACK", "NEXT")
        self.page_control.next_button.set_sensitive(False)
        self.pack_end(self.page_control, False, False, 0)
        self.page_control.connect("next-button-clicked", self.next_page)
        self.page_control.connect("back-button-clicked", self.prev_page)

        title = Heading('Character creator', 'Choose a cool name and secure password')
        self.pack_start(title.container, False, False, 0)

        # This time we need the picture with the login screen to one side.
        image_viewer = ImageView(self)
        self.pack_start(image_viewer, False, False, 0)

        # Get character image.  This hardcoding needs to be removed
        filename = os.path.join(os.path.expanduser('~'),
                                "avatar-content/avatar_inc_env_page2.png")
        image_viewer.set_image(filename)
        self.data_screen = GetData2()
        self.data_screen.connect("widgets-filled", self.enable_next)
        self.data_screen.connect("widgets-empty", self.disable_next)

        # Put it with the same y coordinate as the menu
        image_viewer.put(self.data_screen, 400, 30)
        self.show_all()

    def _show_error_dialog(self, title, description):
        kdialog = KanoDialog(title, description,
                             parent_window=self.win)
        kdialog.run()

    def next_page(self, widget):
        age, bday_date, error = self.data_screen.calculate_age()

        if age == -1:
            self._show_error_dialog(error[0], error[1])
            return

        data = self.data_screen.get_entry_data()

        password = data["password"]
        # If the password entry has less than 6 characters,
        if len(password) < 6:
            self._show_error_dialog(
                "Your password isn't long enough!",
                "It needs to be at least 6 characters long."
            )
            return

        self.win.data = data
        self.data_screen.save_username_and_birthday()

        self.win.remove_main_widget()
        RegistrationScreen3(self.win, age)

    def prev_page(self, widget):
        self.win.remove_main_widget()
        RegistrationScreen1(self.win)

    def enable_next(self, widget):
        self.page_control.enable_next()

    def disable_next(self, widget):
        self.page_control.disable_next()


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

        # This time we need the picture with the login screen to one side.
        image_viewer = ImageView(self)
        self.pack_start(image_viewer, False, False, 0)

        # Get character image
        filename = os.path.join(os.path.expanduser('~'),
                                "avatar-content/avatar_inc_env_page2.png")
        image_viewer.set_image(filename)

        # Pass age into the Data screen - decide whether to ask for Guardian or
        # user email
        self.data_screen = GetData3(age)
        self.data_screen.connect("widgets-filled", self.enable_next)
        self.data_screen.connect("widgets-empty", self.disable_next)

        # Put it with the same y coordinate as the menu
        image_viewer.put(self.data_screen, 400, 30)

        self.show_all()

    def prev_page(self, widget):
        self.data_screen.cache_emails()
        self.win.remove_main_widget()
        page = RegistrationScreen2(self.win)
        self.win.set_main_widget(page)

    def enable_next(self, widget):
        self.page_control.enable_next()

    def disable_next(self, widget):
        self.page_control.disable_next()

    def get_data(self):
        self.win.data.update(self.data_screen.get_entry_data())

    def register_handler(self, widget=None, arg=None):
        self.data_screen.cache_emails()
        self.page_control.disable_buttons()
        self.data_screen.disable_all()
        self.get_data()

        # Make cursor into a spinner
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.win.get_window().set_cursor(watch_cursor)

        if not is_internet():
            # this will launch dialogs until either the user
            # connects to internet or quits
            self.try_to_connect_to_internet()

        def lengthy_process():
            (title, description, return_value) = self.register_user()

            def done():
                # the values for tile, description and return_value are
                # accessible since this function's namespace directly
                # inherits from the function above
                self.win.get_window().set_cursor(None)
                kdialog = KanoDialog(
                    title,
                    description,
                    parent_window=self.win
                )
                kdialog.run()

                if return_value == 1:
                    # If we succeed quit the program
                    Gtk.main_quit()
                else:
                    # If we encountered a problem, allow the user to
                    # fix the issue and retry
                    self.data_screen.enable_all()
                    self.page_control.enable_buttons()

            GObject.idle_add(done)

        if is_internet():
            # only register if there is internet
            thread = threading.Thread(target=lengthy_process)
            thread.start()
        else:
            Gtk.main_quit()

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
                print "keep_checking before {}".format(keep_checking)
                keep_checking = self.keep_trying_to_connect()
                print "keep_checking after {}".format(keep_checking)

        else:
            # exit app
            print "Exiting"
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

    ###################################################

    def register_user(self):

        email = self.win.data["email"]

        # use this in update of registration
        secondary_email = self.win.data["secondary_email"]
        username = self.win.data["username"]
        password = self.win.data["password"]
        date_year = self.win.data["year"]
        date_month = self.win.data["month"]
        date_day = self.win.data["day"]

        logger.info('trying to register user')

        success, text = register_(email, username, password,
                                  date_year, date_month, date_day,
                                  secondary_email=secondary_email)

        if not success:
            logger.info('problem with registration: {}'.format(text))
            title = "Houston, we have a problem"
            description = str(text)
            return_value = 0

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
            return_value = 1

        return (title, description, return_value)
