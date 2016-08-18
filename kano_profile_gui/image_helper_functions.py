#!/usr/bin/env python

# image_.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen

import os
from gi.repository import Gtk
from kano_profile_gui.paths import media_dir


def create_translucent_layer(width, height):
    translucent_layer = Gtk.EventBox()
    translucent_layer.get_style_context().add_class('locked_translucent')
    translucent_layer.set_size_request(width, height)
    return translucent_layer


def get_image_path_at_size(category, name, width, height, locked):

    size_dir = str(width) + 'x' + str(height)

    if locked:
        name = name + "_locked"

    path = os.path.join(
        media_dir,
        "images/badges",
        size_dir,
        category,
        name + '.png'
    )
    return path
