#!/usr/bin/env python

# home_picture.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size of the pictures displayed on the environment page

# Size: width = 230px, height = 180px

# Read from directory /usr/share/kano-profile/media/environments/*

from gi.repository import Gtk, GdkPixbuf
import kano_profile_gui.components.constants as constants
import kano_profile_gui.swags as swags


class Picture():
    def __init__(self):

        self.background_width = 690
        self.background_height = 540
        self.avatar_width = self.background_height
        self.avatar_height = self.background_height

        # Default background and avatar
        environment_filename = constants.media + "/images/environments/1000/environment-1.png"
        avatar_filename = constants.media + "/images/avatars/" + str(self.avatar_width) + "/Avatar-pong-1.png"

        if swags.swag_ui is not None:
            environment_filename = swags.swag_ui.categories[0].get_equipped().filename
            avatar_filename = swags.swag_ui.categories[1].get_equipped().filename

        self.background = Gtk.Image()
        self.background.set_from_file(environment_filename)

        self.avatar = Gtk.Image()
        self.avatar.set_from_file(avatar_filename)
        #pixbuf = GdkPixbuf.Pixbuf.new_from_file(avatar_filename)
        #self.avatar.set_from_pixbuf(pixbuf)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.background_width, self.background_height)
        self.fixed.put(self.background, 0, 0)
        self.fixed.put(self.avatar, (self.background_width - self.avatar_width) / 2, 0)
