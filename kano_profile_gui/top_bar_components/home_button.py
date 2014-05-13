#!/usr/bin/env python

# home_button.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the button styling in the default introduction screen which shows all the settings

from gi.repository import Gtk, Gdk
import kano_profile_gui.components.constants as constants
from kano.world.functions import get_mixed_username
from kano.profile.badges import calculate_kano_level
from kano_profile_gui.images import get_image
from kano.profile.profile import get_avatar


class HomeButton():
    def __init__(self):

        self.img_height = 54
        self.img_width = 54

        # Contains the info about the level and the image
        self.container = Gtk.Grid()

        # Get username here
        self.username = get_mixed_username()

        level, progress = calculate_kano_level()

        # Info about the different settings
        self.title = Gtk.Label(self.username)
        self.title.get_style_context().add_class("home_button_title")
        self.title.get_style_context().add_class("active_label")
        self.title.set_alignment(xalign=0, yalign=1)

        self.description = Gtk.Label("Level " + str(level))
        self.description.get_style_context().add_class("home_button_description")
        self.description.get_style_context().add_class("active_label")
        self.description.set_alignment(xalign=0, yalign=0)

        self.button = Gtk.Button()
        self.button.get_style_context().add_class("home_button")
        self.button.set_can_focus(False)

        self.avatar = Gtk.Fixed()
        self.avatar.set_size_request(60, 60)

        self.img_base = Gtk.Image()
        self.img_base.set_from_file(constants.media + "/images/avatars/avatar-base.png")
        self.img = Gtk.Image()
        subcat, name = get_avatar()
        filename = get_image("avatars", subcat, name + "_circular", str(self.img_width) + 'x' + str(self.img_height))
        self.img.set_from_file(filename)

        self.avatar.put(self.img_base, 0, 0)
        self.avatar.put(self.img, 3, 3)

        self.container.attach(self.title, 2, 0, 1, 1)
        self.container.attach(self.description, 2, 1, 1, 1)
        self.container.attach(self.avatar, 0, 0, 2, 2)
        self.container.set_column_spacing(20)
        self.container.props.valign = Gtk.Align.CENTER

        self.button.add(self.container)

        self.button.height = 100
        self.button.width = 230

        self.button.set_size_request(self.button.width, self.button.height)

    def update(self):
        level, progress = calculate_kano_level()
        self.description.set_text("Level " + str(level))
        self.set_image()

    def set_image(self):
        subcat, name = get_avatar()
        filename = get_image("avatars", subcat, name + "_circular", str(self.img_width) + 'x' + str(self.img_height))
        self.img.set_from_file(filename)

    def set_activate(self, activate):
        title_style = self.title.get_style_context()
        description_style = self.description.get_style_context()
        if activate:
            description_style.remove_class("inactive_label")
            title_style.remove_class("inactive_label")
            description_style.add_class("active_label")
            title_style.add_class("active_label")
        else:
            description_style.remove_class("active_label")
            title_style.remove_class("active_label")
            description_style.add_class("inactive_label")
            title_style.add_class("inactive_label")

        self.title.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("green"))
        self.description.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("green"))
