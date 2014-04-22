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

        self.background_width = 690 + 44
        self.background_height = 540 + 44
        self.avatar_width = 300
        self.avatar_height = 300

        environment_filename = constants.media + "/environments/environment-1.png"
        avatar_filename = constants.media + "/avatars/avatar-1.png"

        #for picture in self.environment_picture:
        # if we have the current active background
        # This will end up defaulting to 1
        if swags.swag_ui is not None:
            environment_filename = swags.swag_ui.environments.get_equipped().filename
            avatar_filename = swags.swag_ui.avatars.get_equipped().filename

        self.background_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(environment_filename, self.background_width, self.background_height)
        self.background = Gtk.Image()
        self.background.set_from_pixbuf(self.background_pixbuf)

        self.avatar_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(avatar_filename, self.avatar_width, self.avatar_height)
        self.avatar = Gtk.Image()
        self.avatar.set_from_pixbuf(self.avatar_pixbuf)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.background_width, self.background_height)
        self.fixed.put(self.background, 0, 0)
        self.fixed.put(self.avatar, 250, 150)
