#!/usr/bin/env python

# navigation_buttons.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# These buttons are the ones along the bottom of the badge screens for
# naviagting between the pages.

import os
from gi.repository import Gtk
from kano_profile_gui.paths import media_dir
from kano.gtk3.cursor import attach_cursor_events


def create_navigation_button(title, position='previous'):
    '''Position is either 'previous', 'middle' or 'end'
    This is to determine the position of the icon on the button.
    Returns a button widget with the title and the icon in the right place.
    '''
    hbox = Gtk.Box()
    button = Gtk.Button()
    button.get_style_context().add_class("navigation_button")

    # If the button is at the end, the icon comes after the label
    if position == "next":
        # next_icon_path is for forward pointing arrow
        next_icon_path = os.path.join(media_dir, "images/icons/next.png")
        icon = Gtk.Image.new_from_file(next_icon_path)
        button.get_style_context().add_class("next")
        label = Gtk.Label(title)

        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(icon, False, False, 0)

    # Otherwise if the icon is at the middle or start,
    # the icon comes before the text
    else:
        if position == "previous":
            # icon_path is for backwards pointing arrow
            icon_path = os.path.join(media_dir, "images/icons/previous.png")
            label = Gtk.Label(title)
            button.get_style_context().add_class("back")

        elif position == "middle":
            # icon_path is for the grid icon
            icon_path = os.path.join(media_dir, "images/icons/grid.png")
            label = Gtk.Label(title)
            button.get_style_context().add_class("middle")

        icon = Gtk.Image.new_from_file(icon_path)
        hbox.pack_start(icon, False, False, 0)
        hbox.pack_start(label, False, False, 0)

    attach_cursor_events(button)
    button.add(hbox)
    return button
