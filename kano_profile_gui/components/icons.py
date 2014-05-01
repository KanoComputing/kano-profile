#!/usr/bin/env python

# icons.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Creates pixbufs that we can use to make images from.  Uses a strip of icons, each 24px by 24px.

from gi.repository import Gtk
import kano_profile_gui.components.constants as constants


# name = ["badges", "challenges", "swag", "next_arrow", "padlock", "locked", "unlocked", "cross"]
def set_from_name(name):
    image = Gtk.Image()
    image.set_from_file(constants.media + "/images/icons/" + name + ".png")
    return image
