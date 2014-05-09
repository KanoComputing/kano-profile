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
import kano_profile_gui.swags as swags
from kano_profile_gui.images import get_image


class HomePicture():
    def __init__(self):

        self.background_width = 734
        self.background_height = 404
        self.avatar_width = self.background_width
        self.avatar_height = self.background_height
        self.background = Gtk.Image()
        self.avatar = Gtk.Image()

        # This should be changed to reading from the function

        if swags.swag_ui is not None and swags.swag_ui.categories[0].get_equipped_picture() is not None and swags.swag_ui.categories[1].get_equipped_picture() is not None:
            environment_file = swags.swag_ui.categories[0].get_equipped_picture().get_filename_at_size(self.background_width, self.background_height)
            avatar_file = swags.swag_ui.categories[1].get_equipped_picture().get_filename_at_size(self.avatar_width, self.avatar_height)
        else:
            a_category = "avatars"
            a_subcategory = "video_dude"
            a_name = "video_dude_2"
            e_category = "environments"
            e_subcategory = "all"
            e_name = "fields_of_ideas"
            environment_file = get_image(e_category, e_subcategory, e_name, str(self.background_width) + 'x' + str(self.background_height))
            avatar_file = get_image(a_category, a_subcategory, a_name, str(self.background_width) + 'x' + str(self.background_height))

        self.background.set_from_file(environment_file)
        self.avatar.set_from_file(avatar_file)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.background_width, self.background_height)
        self.fixed.put(self.background, 0, 0)
        self.fixed.put(self.avatar, (self.background_width - self.avatar_width) / 2, 0)
