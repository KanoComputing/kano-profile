#!/usr/bin/env python

# home_picture.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size of the pictures displayed on the environment page

# Size: width = 734px, height = 404px

# Read from directory /usr/share/kano-profile/media/environments/*

from gi.repository import Gtk
import kano_profile_gui.components.constants as constants
import kano_profile_gui.swags as swags


class HomePicture():
    def __init__(self):

        self.background_width = 734
        self.background_height = 404
        self.avatar_width = self.background_width
        self.avatar_height = self.background_height
        self.background = Gtk.Image()
        self.avatar = Gtk.Image()

        if swags.swag_ui is not None:
            environ_file = swags.swag_ui.categories[0].get_equipped().get_filename_at_size(self.background_width, self.background_height)
            self.background.set_from_file(environ_file)
            avatar_file = swags.swag_ui.categories[1].get_equipped().get_filename_at_size(self.avatar_width, self.avatar_height)
            self.avatar.set_from_file(avatar_file)
        else:
            environment_filename = constants.media + "/images/environments/" + str(self.background_width) + "x" + str(self.background_height) + "/arcade_hall.png"
            print environment_filename
            avatar_filename = constants.media + "/images/avatars/" + str(self.avatar_width) + "x" + str(self.avatar_height) + "/video_guy.png"
            print avatar_filename
            self.background.set_from_file(environment_filename)
            self.avatar.set_from_file(avatar_filename)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.background_width, self.background_height)
        self.fixed.put(self.background, 0, 0)
        self.fixed.put(self.avatar, (self.background_width - self.avatar_width) / 2, 0)
