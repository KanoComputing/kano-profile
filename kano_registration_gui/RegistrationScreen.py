# RegistrationScreen.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This is the screen that is shown when you register for Kano World


import subprocess

from gi.repository import Gtk

from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from kano.gtk3.kano_dialog import KanoDialog
from kano.logging import logger
from kano.network import is_internet
from kano.utils import run_bg

from kano_profile.paths import bin_dir
from kano_profile.tracker import save_hardware_info, save_kano_version, \
    track_data
from kano_registration_gui.GetData import GetData

from kano_world.functions import content_type_json, request_wrapper
from kano_world.functions import register as register_


class RegistrationScreen(Gtk.Box):
    """
    """

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_main_widget(self)
        self.win.set_decorated(True)

        title = Heading(
            _("Kano World"),
            _("Choose a cool name and secure password")
        )
        self.pack_start(title.container, False, False, 0)

        self.data_screen = GetData()  # TODO: refactor this
        self.data_screen.connect('widgets-filled', self._enable_register_button)
        self.data_screen.connect('widgets-empty', self._disable_register_button)
        self.add(self.data_screen)

        self.register_button = KanoButton(_("JOIN KANO WORLD"))
        self.register_button.set_sensitive(False)
        self.register_button.set_margin_top(10)
        self.register_button.set_margin_left(30)
        self.register_button.set_margin_right(30)
        self.register_button.set_margin_bottom(30)
        self.register_button.connect('clicked', self._on_register_button)
        self.pack_end(self.register_button, False, False, 0)

        self.win.show_all()

    def _enable_register_button(self, widget=None):
        """
        """
        self.register_button.set_sensitive(True)

    def _disable_register_button(self, widget=None):
        """
        """
        self.register_button.set_sensitive(False)

    def _on_register_button(self, widget=None):  # TODO: refactor this
        """
        """
        if not is_internet():
            self._show_not_internet_dialog()
            return

        # Get the username, password and birthday
        data = self.data_screen.get_widget_data()
        username = data['username']

        if not self._is_username_available(username):
            self._show_username_taken_dialog(username)
            return

        # We can save the username to kano-profile
        # Don't save password as this is private
        self.data_screen.save_username_and_birthday()  # TODO: rename this
        self.data_screen.cache_emails()
        data = self.data_screen.get_widget_data()

        # This means no threads are needed.
        while Gtk.events_pending():  # TODO: why is this needed?
            Gtk.main_iteration()

        # Try and register the account on the server
        email = data['email']
        username = data['username']
        password = data['password']

        success, text = register_(email, username, password,
                                  marketing_enabled=True)

        # This should no longer be needed, since this is checked in the first
        # screen. However there is a small chance someone could take the
        # username while the user is in the process of registering
        if not success:
            if text.strip() == _("Cannot register, problem: " \
               "Username already registered"):

                self._show_username_taken_dialog(username)

            else:
                logger.info("problem with registration: {}".format(text))
                return_value = 'FAIL'
                self._create_dialog(
                    title=_("Houston, we have a problem"),
                    description=str(text)
                )
                track_data('world-registration-failed', {'reason': text})

        else:
            logger.info("registration successful")

            # saving hardware info and initial Kano version
            save_hardware_info()
            save_kano_version()

            # running kano-sync after registration
            logger.info("running kano-sync after successful registration")
            cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            run_bg(cmd)

            return_value = 'SUCCEED'
            self._create_dialog(
                title=_("Profile activated!"),
                description=_("Now you can share stuff, build your character, " \
                              "and connect with friends.")
            )

        self.win.get_window().set_cursor(None)

        # Close the app if it was successful
        if return_value == 'SUCCEED':
            Gtk.main_quit()

    def _is_username_available(self, name):
        """
        Returns True if username is available, and False otherwise
        """
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

    def _create_dialog(self, title, description):  # TODO: refactor this
        kdialog = KanoDialog(
            title,
            description,
            parent_window=self.win
        )
        rv = kdialog.run()
        return rv

    def _show_error_dialog(self, title, description):  # TODO: refactor this
        kdialog = KanoDialog(
            title,
            description,
            parent_window=self.win
        )
        kdialog.run()

    def _show_username_taken_dialog(self, username):  # TODO: refactor this
        track_data('world-registration-username-taken', {'username': username})
        kd = KanoDialog(
            _("This username is taken!"),
            _("Try another one"),
            parent_window=self.win
        )
        kd.run()
        self.data_screen.username.set_text("")
        self.data_screen.validate_username()
        self._disable_register_button()
        self.data_screen.username.grab_focus()

    def _show_not_internet_dialog(self):  # TODO: refactor this
        kd = KanoDialog(
            _("You don't have internet"),
            _("Do you want to connect to WiFi?"),
            [
                {
                    'label': _("YES"),
                    'color': 'green',
                    'return_value': 0
                },
                {
                    'label': _("NO"),
                    'color': 'red',
                    'return_value': 1
                }
            ],
            parent_window=self.win
        )
        response = kd.run()

        # Close the dialog
        while Gtk.events_pending():  # TODO: why is this needed?
            Gtk.main_iteration()

        if response == 0:
            subprocess.Popen("sudo kano-wifi-gui", shell=True)
