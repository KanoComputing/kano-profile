#!/usr/bin/env python

# swag_screen.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Shows profile created
#

import sys
from kano_login.templates.template import Template
from kano_login.data import get_data
from kano_profile_gui.images import get_image
from kano_world.functions import is_registered


class SwagScreen():

    profile_created_data = get_data("PROFILE_CREATED")
    no_profile_data = get_data("NO_PROFILE")

    def __init__(self, win):
        # Set window
        self.win = win
        self.win.set_decorated(False)
        self.win.set_resizable(True)
        # Set text depending on login
        login = is_registered()
        if login:
            header = self.profile_created_data["LABEL_1"]
            subheader = self.profile_created_data["LABEL_2"]
            image = self.profile_created_data["TOP_PIC"]
            button = self.profile_created_data["KANO_BUTTON"]
        else:
            header = self.no_profile_data["LABEL_1"]
            subheader = self.no_profile_data["LABEL_2"]
            image = self.no_profile_data["TOP_PIC"]
            button = self.no_profile_data["KANO_BUTTON"]
        # Set image
        img_width = 590
        img_height = 270
        image_filename = get_image("login", "", image, str(img_width) + 'x' + str(img_height))
        # Create template
        self.template = Template(image_filename, header, subheader, button, "")

        self.win.set_main_widget(self.template)
        self.template.kano_button.connect("button_release_event", self.next_screen)
        self.template.kano_button.connect("key_release_event", self.next_screen)
        self.template.button_box.set_margin_bottom(30)
        self.template.kano_button.grab_focus()
        self.win.show_all()

    def next_screen(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            # Exit
            sys.exit(0)
