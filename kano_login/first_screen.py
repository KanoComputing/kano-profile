#!/usr/bin/env python

# first_screen.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# First screen of profile on first run
# Launched on straight after kano-settings
# Dependent on internet connection

import os
from gi.repository import Gtk

from kano.gtk3.buttons import KanoButton, OrangeButton
from kano.gtk3.heading import Heading
from kano_login.login import Login
from kano_login.templates.template import Template
from kano_login.swag_screen import SwagScreen
from kano.network import is_internet
from kano_profile_gui.images import get_image
from kano_registration_gui.RegistrationScreen1 import RegistrationScreen1


class FirstScreenTemplate(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        kano_button_text = "CREATE"
        skip_button_text = "Skip"
        login_button_text = "I have a profile"
        header = "Now let's make a cool Profile"
        subheader = "So you can save badges, games, and projects"
        img_width = 590
        img_height = 270

        self.skip_button = OrangeButton(skip_button_text)
        self.login_button = OrangeButton(login_button_text)

        image_filename = get_image(
            "login", "", "first-screen", str(img_width) + 'x' + str(img_height)
        )
        self.image = Gtk.Image.new_from_file(image_filename)
        self.pack_start(self.image, False, False, 0)

        self.heading = Heading(header, subheader)
        self.kano_button = KanoButton(kano_button_text)

        self.pack_start(self.heading.container, False, False, 0)

        self.button_box = Gtk.ButtonBox(spacing=10)
        self.button_box.set_layout(Gtk.ButtonBoxStyle.SPREAD)
        self.pack_start(self.button_box, False, False, 0)

        self.button_box.pack_start(self.login_button, False, False, 0)
        self.button_box.pack_start(self.kano_button, False, False, 0)
        self.button_box.pack_start(self.skip_button, False, False, 0)


class FirstScreen(FirstScreenTemplate):
    def __init__(self, win, dummy=None):

        FirstScreenTemplate.__init__(self)

        self.win = win
        self.win.set_decorated(False)
        self.win.set_main_widget(self)

        self.kano_button.connect("button_release_event", self.register_screen)
        self.login_button.connect(
            "button_release_event", self.login_screen
        )
        self.skip_button.connect(
            "button_release_event", self.exit_registration
        )

        self.kano_button.connect(
            "key_release_event", self.register_screen
        )
        self.button_box.set_margin_bottom(30)
        self.kano_button.grab_focus()
        self.win.show_all()

    def login_screen(self, widget, event):
        self.win.remove_main_widget()

        if is_internet():
            Login(win=self.win, prev_screen=None, first_boot=True)
        else:
            NoInternet(self.win)

    def register_screen(self, widget, event):

        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.win.remove_main_widget()
            RegistrationScreen1(self.win)

    def exit_registration(self, widget, event):
        self.win.remove_main_widget()
        SwagScreen(self.win)

    def repack(self):
        self.win.remove_main_widget()
        self.win.set_main_widget(self.template)


class NoInternet(Template):
    def __init__(self, win):

        self.win = win
        self.win.set_decorated(False)

        img_width = 590
        img_height = 270

        header = "Oops! You need Internet to make a profile"
        subheader = "But you can skip this if you have no connection right now"
        image_filename = get_image("login", "", "no-internet",
                                   str(img_width) + 'x' + str(img_height))
        kano_button_label = "CONNECT"
        orange_button_label = "Register later"

        Template.__init__(self, header, subheader, image_filename,
                          kano_button_label, orange_button_label)

        self.win.set_main_widget(self.template)
        self.kano_button.connect("button_release_event", self.connect)

        # Since cannot pass with keyboard, set it so it cannot receive
        # keyboard focus
        self.kano_button.set_can_focus(False)

        self.orange_button.connect("button_release_event", self.register_later)
        self.kano_button.grab_focus()
        self.win.show_all()

    def connect(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            # Launch kano-wifi
            os.system('sudo /usr/bin/kano-wifi-gui')

            self.win.remove_main_widget()
            FirstScreen(self.win)

    def register_later(self, widget, event):
        self.win.remove_main_widget()
        SwagScreen(self.win)
