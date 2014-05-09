#!/usr/bin/env python

# home_button.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the button styling in the default introduction screen which shows all the settings

from gi.repository import Gtk
import kano_profile_gui.components.constants as constants
from kano.world.functions import get_mixed_username
from kano.profile.badges import calculate_kano_level


class HomeButton():
    def __init__(self):

        # Contains the info about the level and the image
        self.container = Gtk.Grid()

        # Get username here
        self.username = get_mixed_username()

        level, progress = calculate_kano_level()

        # Info about the different settings
        self.title = Gtk.Label(self.username)
        self.title.get_style_context().add_class("home_button_title")
        self.title.set_alignment(xalign=0, yalign=1)

        self.description = Gtk.Label("Level " + str(level))
        self.description.get_style_context().add_class("home_button_description")
        self.description.set_alignment(xalign=0, yalign=0)

        self.button = Gtk.Button()
        self.button.get_style_context().add_class("top_bar_button")
        self.button.get_style_context().add_class("home_button")
        self.button.set_can_focus(False)
        self.img = Gtk.Image()
        self.img.set_from_file(constants.media + "/images/avatars/avatar-base.png")

        self.container.attach(self.title, 2, 0, 1, 1)
        self.container.attach(self.description, 2, 1, 1, 1)
        self.container.attach(self.img, 0, 0, 2, 2)
        self.container.set_column_spacing(20)
        self.container.props.valign = Gtk.Align.CENTER

        self.button.add(self.container)

        self.button.height = 100
        self.button.width = 250

        self.button.set_size_request(self.button.width, self.button.height)

    def update_level(self, level_number):
        self.level_image.set_from_file(constants.media + "/icons/Level-" + str(level_number) + ".png")
        self.level.set_text("Level " + str(level_number))
        self.earned_title.set_text(self.possible_titles[level_number])
