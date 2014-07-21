
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


class SetupSuccessful():
    def __init__(self, win):

        self.win = win
        self.template = Template(None, "Setup successful!", "You can change the sound, screen size, and more any time by clicking on Settings in the bottom bar ", "CONTINUE", "")

        self.win.add(self.template)
        self.template.kano_button.connect("button_release_event", self.next_screen)
        self.win.set_size_request(590, 200)
        self.win.show_all()

    def next_screen(self, widget, event):
        self.win.clear_win()
        self.win.set_size_request(590, 450)
        FirstScreen(self.win)