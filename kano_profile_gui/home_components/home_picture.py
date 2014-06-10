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
from kano_profile_gui.images import get_image
from kano_profile.profile import get_avatar, get_environment


class HomePicture():
    def __init__(self):

        self.background_width = 734
        self.background_height = 404
        self.avatar_width = self.background_width
        self.avatar_height = self.background_height
        self.background = Gtk.Image()
        self.avatar = Gtk.Image()

        # This should be changed to reading from the function
        a_subcategory, a_name = get_avatar()
        e_name = get_environment()

        environment_file = get_image("environments", "all", e_name, str(self.background_width) + 'x' + str(self.background_height))
        avatar_file = get_image("avatars", a_subcategory, a_name, str(self.background_width) + 'x' + str(self.background_height))

        self.background.set_from_file(environment_file)
        self.avatar.set_from_file(avatar_file)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.background_width, self.background_height)
        self.fixed.put(self.background, 0, 0)
        self.fixed.put(self.avatar, (self.background_width - self.avatar_width) / 2, 0)
