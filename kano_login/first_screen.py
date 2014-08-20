
#!/usr/bin/env python

# first_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# First screen of profile on first run
# Launched on straight after kano-settings
# Dependent on internet connection

#from gi.repository import Gtk

import os
import sys
from kano_login.login import Login
from kano_login.about_you import AboutYou
from kano_login.templates.template import Template
from kano_login.data import get_data
from kano.network import is_internet
from kano_profile_gui.images import get_image


def create_template(string):
    data = get_data(string)
    img_width = 590
    img_height = 270

    header = data["LABEL_1"]
    subheader = data["LABEL_2"]
    image_filename = get_image("login", "", data["TOP_PIC"], str(img_width) + 'x' + str(img_height))
    kano_button_label = data["KANO_BUTTON"]
    orange_button_label = data["ORANGE_BUTTON"]
    template = Template(image_filename, header, subheader, kano_button_label, orange_button_label)
    return template


class FirstScreen():
    def __init__(self, win):

        self.win = win
        self.win.reset_allocation()

        self.template = create_template("FIRST_SCREEN")
        self.win.set_main_widget(self.template)
        self.template.kano_button.connect("button_release_event", self.next_screen)
        self.template.orange_button.connect("button_release_event", self.login_screen)
        self.template.kano_button.connect("key_release_event", self.next_screen)
        self.template.button_box.set_margin_bottom(30)
        self.template.kano_button.grab_focus()
        self.win.show_all()

    def login_screen(self, widget, event):
        self.win.clear_win()

        if is_internet():
            Login(self.win)
        else:
            NoInternet(self.win)

    def next_screen(self, widget, event):

        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.win.clear_win()

            if is_internet():
                AboutYou(self.win, self)
            else:
                NoInternet(self.win)

    def repack(self):
        self.win.clear_win()
        self.win.set_main_widget(self.template)


class NoInternet():
    def __init__(self, win):

        self.win = win
        self.template = create_template("NO_INTERNET")

        self.win.set_main_widget(self.template)
        self.template.kano_button.connect("button_release_event", self.connect)

        # Since cannot pass with keyboard, set it so it cannot receive keyboard focus
        self.template.kano_button.set_can_focus(False)

        # For now, remove keyboard event listener as is interfering with kano-connect
        #self.template.kano_button.connect("key_release_event", self.connect)

        self.template.orange_button.connect("button_release_event", self.register_later)
        self.template.kano_button.grab_focus()
        self.win.show_all()

    def connect(self, widget, event):
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            # Launch kano-wifi
            os.system('rxvt -title \'WiFi Setup\' -e sudo /usr/bin/kano-wifi')

            self.win.clear_win()
            FirstScreen(self.win)

    def register_later(self, widget, event):
        sys.exit(0)
