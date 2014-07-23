
#!/usr/bin/env python

# setup_successful.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# First screen of profile on first run
# Launched on straight after kano-settings
# Dependent on internet connection

from kano_login.first_screen import FirstScreen
from kano_login.templates.template import Template
from kano_login.data import get_data


class SetupSuccessful():

    data = get_data("SETUP_SUCCESSFUL")

    def __init__(self, win):

        self.win = win
        self.template = Template(None, self.data["LABEL_1"], self.data["LABEL_2"], self.data["KANO_BUTTON"], "")

        self.win.add(self.template)
        self.template.kano_button.connect("button_release_event", self.next_screen)
        self.win.set_size_request(590, 200)
        self.win.show_all()

    def next_screen(self, widget, event):
        self.win.clear_win()
        self.win.set_size_request(590, 450)

        # Hacky way of moving the window back to the centre
        # Get current coordinates, then move the window up by 100 pixels
        x, y = self.win.get_position()
        self.win.move(x, y - 100)
        FirstScreen(self.win)
