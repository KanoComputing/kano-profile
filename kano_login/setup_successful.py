
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
from kano_profile_gui.images import get_image


class SetupSuccessful():

    data = get_data("SETUP_SUCCESSFUL")

    def __init__(self, win):

        self.win = win
        self.win.set_resizable(True)

        img_width = 590
        img_height = 270
        image_filename = get_image("login", "", self.data["TOP_PIC"], str(img_width) + 'x' + str(img_height))
        self.template = Template(image_filename, self.data["LABEL_1"], self.data["LABEL_2"], self.data["KANO_BUTTON"], "")

        self.win.set_main_widget(self.template)
        self.template.kano_button.connect("button_release_event", self.next_screen)
        self.template.kano_button.connect("key_release_event", self.next_screen)
        self.template.button_box.set_margin_bottom(30)
        self.win.show_all()

    def next_screen(self, widget, event):
        # If enter key is pressed or mouse button is clicked
        if not hasattr(event, 'keyval') or event.keyval == 65293:
            self.win.clear_win()
            FirstScreen(self.win)
