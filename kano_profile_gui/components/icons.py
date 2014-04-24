#!/usr/bin/env python

# icons.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Creates pixbufs that we can use to make images from.  Uses a strip of icons, each 24px by 24px.

from gi.repository import Gtk, GdkPixbuf
import kano_profile_gui.components.constants as constants

# To make an image using the pixbuf icon, use the command below:
# image.set_from_pixbuf(self.pixbuf)


def set_from_name(name):
    icon_number = 0
    if name == "badge":
        icon_number = 0
    elif name == "challenge":
        icon_number = 1
    elif name == "swag":
        icon_number = 2
    elif name == "next_arrow":
        icon_number = 3
    elif name == "prev_arrow":
        icon_number = 4
    elif name == "locked":
        icon_number = 5
    elif name == "cross":
        icon_number = 6
    elif name == "unlocked":
        icon_number = 7
    # Create main window
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(constants.media + '/images/icons/systemsetup-icons.png', 192, 24)
    subpixbuf = pixbuf.new_subpixbuf(24 * icon_number, 0, 24, 24).add_alpha(True, 255, 255, 255)
    image = Gtk.Image()
    image.set_from_pixbuf(subpixbuf)
    return image
