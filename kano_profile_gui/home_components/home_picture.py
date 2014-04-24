#!/usr/bin/env python

# home_picture.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size of the pictures displayed on the environment page

# Size: width = 230px, height = 180px

# Read from directory /usr/share/kano-profile/media/environments/*

from gi.repository import Gtk
import kano_profile_gui.components.constants as constants
import kano_profile_gui.swags as swags


class Picture():
    def __init__(self):

        self.background_width = 690
        self.background_height = 540
        self.avatar_width = self.background_height
        self.avatar_height = self.background_height

        if swags.swag_ui is not None:
            self.background = swags.swag_ui.categories[0].get_equipped().set_image_width(690)
            self.avatar = swags.swag_ui.categories[1].get_equipped().set_image_width(580)
        else:
            environment_filename = constants.media + "/images/690/environments/Kano-environment1.png"
            avatar_filename = constants.media + "/images/avatars/580/Avatar-1.png"
            self.background = Gtk.Image()
            self.background.set_from_file(environment_filename)
            self.avatar = Gtk.Image()
            self.avatar.set_from_file(avatar_filename)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.background_width, self.background_height)
        self.fixed.put(self.background, 0, 0)
        self.fixed.put(self.avatar, (self.background_width - self.avatar_width) / 2, 0)
