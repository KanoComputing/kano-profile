#!/usr/bin/env python

# icons.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Creates pixbufs that we can use to make images from.  Uses a strip of icons, each 24px by 24px.

import os
from gi.repository import Gtk, GdkPixbuf
from kano_profile_gui.paths import media_dir


# name = ["badges", "challenges", "swag", "next_arrow", "padlock", "locked", "unlocked", "cross"]
def set_from_name(name):
    image = Gtk.Image()
    image.set_from_file(media_dir + "/images/icons/" + name + ".png")
    return image

MEDIA_LOCS = ['../media', '/usr/share/kano-profile/media']
APP_ICON_SIZE = 68


def get_app_icon(loc, size=APP_ICON_SIZE):
    try:
        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(loc, size, size)
        icon = Gtk.Image.new_from_pixbuf(pb)
    except:
        icon = Gtk.Image.new_from_icon_name(loc, -1)
        icon.set_pixel_size(size)

    return icon


def get_ui_icon(name):
    if name == 'green_arrow':
        icon_number = 0
    elif name == 'pale_right_arrow':
        icon_number = 1
    elif name == 'dark_left_arrow':
        icon_number = 2
    elif name == 'dark_right_arrow':
        icon_number = 3
    elif name == 'pale_left_arrow':
        icon_number = 4
    elif name == 'tick':
        icon_number = 5
    elif name == 'cross':
        icon_number = 6
    elif name == 'dropdown_arrow':
        icon_number = 7
    else:
        raise Exception('Unknown icon name ' + name)

    src_loc = os.path.join(media_dir, 'images/icons/systemsetup-icons.png')
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(src_loc, 192, 24)

    subpixbuf = pixbuf.new_subpixbuf(24 * icon_number, 0, 24, 24)
    buf = subpixbuf.add_alpha(True, 255, 255, 255)

    icon = Gtk.Image()
    icon.set_from_pixbuf(buf)
    return icon
