#!/usr/bin/env python

# login.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for login screen

import threading
import sys
from gi.repository import Gtk, Gdk, GObject

from kano.network import is_internet
from kano.logging import logger

from kano.utils import run_bg
from kano.gtk3.buttons import KanoButton
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.heading import Heading
from kano.gtk3.labelled_entries import LabelledEntries

from kano_profile.paths import bin_dir
from kano_profile.profile import load_profile, save_profile_variable
from kano_profile.tracker import save_hardware_info, save_kano_version
from kano_world.functions import (login as login_, is_registered,
                                  reset_password, get_email,
                                  get_mixed_username)

from kano_login.templates.kano_button_box import KanoButtonBox
from kano_login.swag_screen import SwagScreen

from kano_registration_gui.RegistrationScreen1 import RegistrationScreen1

profile = load_profile()
force_login = is_registered() and 'kanoworld_username' in profile


class Login(Gtk.Box):
    width = 550

    def __init__(self, win, prev_screen=None, first_boot=False):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_main_widget(self)
        self.win.set_decorated(True)
        self.win.set_size_request(self.width, -1)
        self.first_boot = first_boot

        self.heading = Heading("Login", "Enter your username and password")
        self.pack_start(self.heading.container, False, False, 10)

        if force_login:
            self.add_username_as_label()

        else:
            self.labelled_entries = LabelledEntries(
                [{"heading": "Username", "subheading": ""},
                 {"heading": "Password", "subheading": ""}]
            )
            self.labelled_entries.set_spacing(15)
            self.labelled_entries.set_margin_right(40)
            self.username_entry = self.labelled_entries.get_entry(0)
            self.password_entry = self.labelled_entries.get_entry(1)
            self.pack_start(self.labelled_entries, False, False, 15)

        self.password_entry.set_visibility(False)

        for entry in self.labelled_entries.get_entries():
            entry.connect("key_release_event", self.enable_kano_button)
            entry.connect("key-release-event", self.activate)

        self.button_box = KanoButtonBox(
            "LOGIN",
            "Create New",
            "Forgotten password?"
        )
        self.button_box.set_spacing(40)
        self.button_box.set_margin_left(80)
        self.button_box.set_margin_bottom(30)
        self.kano_button = self.button_box.kano_button
        self.button_box.set_orange_button_cb(self.go_to_registration)
        self.button_box.set_orange_button2_cb(self.reset_password_screen)
        self.kano_button.connect("button_release_event", self.activate)
        self.kano_button.connect("key-release-event", self.activate)
        self.pack_start(self.button_box, False, False, 20)

        self.kano_button.set_sensitive(False)

        if not force_login:
            self.username_entry.grab_focus()
        else:
            self.password_entry.grab_focus()

        self.win.show_all()

    def add_username_as_label(self):
        '''This replaces the username entry with a label conatining the
        username.
        '''
        username = get_mixed_username()
        title_label = Gtk.Label(" Username:  ")
        self.username_label = Gtk.Label(username)
        title_label.get_style_context().add_class("bold_label")
        self.username_label.get_style_context().add_class("desc_label")

        hbox = Gtk.Box()
        hbox.pack_start(title_label, False, False, 0)
        hbox.pack_start(self.username_label, False, False, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(hbox, False, False, 0)
        align = Gtk.Alignment(xscale=0, xalign=0.5)
        align.add(vbox)

        # Needs adjustment
        align.set_padding(0, 0, 100, 0)

        self.pack_start(align, False, False, 15)
        self.labelled_entries = LabelledEntries(
            [{"heading": "Password", "subheading": ""}]
        )
        self.password_entry = self.labelled_entries.get_entry(0)
        vbox.pack_start(self.labelled_entries, False, False, 15)

    def enable_kano_button(self, widget=None, event=None):
        '''This enables the login button if both the username entry
        and password entry are non empty.
        This is linked to the key-release-event on the password and username
        entries.
        '''
        text0 = self.get_username_input()
        text1 = self.password_entry.get_text()
        if text0 != "" and text1 != "":
            self.kano_button.set_sensitive(True)
        else:
            self.kano_button.set_sensitive(False)

    def get_username_input(self):
        '''Get the username text from the username entry or label.
        '''
        if force_login:
            text = self.username_label.get_text()
        else:
            text = self.username_entry.get_text()
        return text

    def repack(self):
        self.win.remove_main_widget()
        self.win.set_main_widget(self)

    def go_to_registration(self, widget, event, args=[]):
        '''Go to the first registration screen.
        '''
        self.win.remove_main_widget()
        RegistrationScreen1(self.win)

    def activate(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self.win.get_window().set_cursor(watch_cursor)
            self.kano_button.start_spinner()
            self.kano_button.set_sensitive(False)

            thread = threading.Thread(target=self.log_user_in)
            thread.start()

    def log_user_in(self):
        if not is_internet():
            title = "You don't have internet!"
            description = (
                "Connect with wifi or ethernet and try again"
            )
            return_value = 0

        else:
            (title, description, return_value) = self.log_user_in_with_internet()

        GObject.idle_add(self.show_login_status_dialog,
                         title, description, return_value)

    def log_user_in_with_internet(self):
        '''If we know the user has internet, attempt to login.
        '''
        username_text = self.get_username_input()
        password_text = self.password_entry.get_text()
        success, text = login_(username_text, password_text)

        if not success:
            logger.info('problem with login: {}'.format(text))
            title = "Houston, we have a problem"
            description = text
            return_value = "FAIL"

        else:
            (title, description, return_value) = self.log_in_success()

        return (title, description, return_value)

    def log_in_success(self):
        '''If the login process is successful, sync with kano world
        and return success dialog text.
        '''
        logger.info('login successful')

        # saving hardware info and initial Kano version
        save_hardware_info()
        save_kano_version()

        # restore on first successful login/restore
        try:
            first_sync_done = profile['first_sync_done']
        except Exception:
            first_sync_done = False

        if not first_sync_done:
            logger.info('running kano-sync --sync && --sync && --restore after first time login')

            # doing first sync and restore
            cmd1 = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            cmd2 = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            cmd3 = '{bin_dir}/kano-sync --restore -s'.format(bin_dir=bin_dir)
            cmd = "{} && {} && {}".format(cmd1, cmd2, cmd3)
            run_bg(cmd)

            save_profile_variable('first_sync_done', True)

        else:
            logger.info('running kano-sync --sync after non-first login')

            # sync on each successful login
            cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            run_bg(cmd)

        title = "Success!"
        description = "You're in - online features now enabled."
        return_value = "SUCCESS"

        return (title, description, return_value)

    def show_login_status_dialog(self, title, description, return_value):
        '''Show a dialog with the title, description and that returns the
        return_value.
        Since this is used at the end of the login process, we also reset
        the cursor and kano button spinner.
        '''
        kdialog = KanoDialog(title, description,
                             {"OK": {"return_value": return_value}},
                             parent_window=self.win)
        response = kdialog.run()

        if response == "SUCCESS":
            if self.first_boot:
                self.win.remove_main_widget()
                SwagScreen(self.win)
            else:
                sys.exit(0)

        # If the login didn't work, try again.
        self.win.get_window().set_cursor(None)
        self.kano_button.stop_spinner()
        self.kano_button.set_sensitive(True)

        if not force_login:
            self.username_entry.grab_focus()

    def reset_password_screen(self, button, event, args):
        self.win.remove_main_widget()
        ResetPassword(self.win)


class ResetPassword(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.win = win
        self.win.set_decorated(False)
        self.win.set_main_widget(self)

        self.heading = Heading(
            "Reset your password",
            "We'll send a new password to your email"
        )
        self.pack_start(self.heading.container, False, False, 10)

        self.labelled_entries = LabelledEntries(
            [{"heading": "Email", "subheading": ""}]
        )
        self.pack_start(self.labelled_entries, False, False, 0)

        # Read email from file
        user_email = get_email()

        self.email_entry = self.labelled_entries.get_entry(0)
        self.email_entry.set_text(user_email)
        self.email_entry.connect("key-release-event", self.activate)

        self.button = KanoButton("RESET PASSWORD")
        self.button.pack_and_align()
        self.button.connect("button-release-event", self.activate)
        self.button.connect("key-release-event", self.activate)
        self.button.set_padding(30, 30, 0, 0)

        self.pack_start(self.button.align, False, False, 0)
        self.win.show_all()

    def activate(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
            self.win.get_window().set_cursor(watch_cursor)
            self.button.set_sensitive(False)
            self.button.start_spinner()

            thread = threading.Thread(target=self.send_new_password)
            thread.start()

    def send_new_password(self):
        # User may change email
        email = self.labelled_entries.get_entry(0).get_text()
        success, text = reset_password(email)
        if success:
            title = "Success!"
            description = "Sent new password to your email"
            button_dict = {
                "GO TO LOGIN SCREEN": {"return_value": 12},
                "QUIT": {"return_value": 10, "color": "red"}
            }
        else:
            title = "Something went wrong!"
            description = text
            button_dict = {
                "QUIT": {"return_value": 10, "color": "red"},
                "TRY AGAIN": {"return_value": 11}
            }

        GObject.idle_add(
            self.finished_thread_cb,
            title,
            description,
            button_dict
        )

    def finished_thread_cb(self, title, description, button_dict):
        kdialog = KanoDialog(
            title,
            description,
            button_dict=button_dict,
            parent_window=self.win
        )
        response = kdialog.run()

        self.win.get_window().set_cursor(None)
        self.button.stop_spinner()
        self.button.set_sensitive(True)

        if response == 10:
            Gtk.main_quit()
        # stay put
        elif response == 11:
            pass
        elif response == 12:
            self.go_to_login_screen()

    def go_to_login_screen(self):
        self.win.remove_main_widget()
        Login(self.win)
