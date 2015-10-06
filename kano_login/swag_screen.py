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
from kano_profile_gui.images import get_image
from kano_world.functions import is_registered


class SwagScreen(Template):
    def __init__(self, win):

        # Set window
        self.win = win
        self.win.set_decorated(False)
        self.win.set_resizable(True)

        # Set text depending on login
        login = is_registered()
        if login:
            header = _("Profile activated!")
            subheader = _(
                u"Now you can share stuff, build your character,"
                u"and connect with friends! You've earned some "
                u"rewards\N{HORIZONTAL ELLIPSIS}"
            )
            image_name = "profile-created"
            button_label = _("Let's go").upper()
        else:
            header = _("No online profile - for now.")
            subheader = _(
                "Your profile stores all your rewards, projects, and "
                "challenges. But fear not - we'll save everything for "
                "when you have internet."
            )
            image_name = "no-profile-new"
            button_label = _("Let's go").upper()

        # Set image
        img_width = 590
        img_height = 270
        image_filename = get_image(
            "login", "", image_name, str(img_width) + 'x' + str(img_height)
        )

        # Create template
        Template.__init__(self, image_filename, header, subheader,
                          button_label, "")

        self.win.set_main_widget(self)
        self.kano_button.connect("button_release_event", self.next_screen)
        self.kano_button.connect("key_release_event", self.next_screen)
        self.kano_button.grab_focus()
        self.win.show_all()

        # Force the cross button to hide
        self.win.headerbar.close_button.hide()

    def next_screen(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            # Exit
            sys.exit(0)
