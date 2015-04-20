#!/usr/bin/env python

# badge_screen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano_profile_gui.paths import media_dir
from kano.gtk3.cursor import attach_cursor_events


def create_navigation_button(title, position='previous'):
    '''position is either 'previous', 'middle' or 'end'
    This is to determine the position of the icon on the button
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
            # button.connect("clicked", self._go_to_other_badge, -1)
            button.get_style_context().add_class("back")

        elif position == "middle":
            # icon_path is for the grid icon
            icon_path = os.path.join(media_dir, "images/icons/grid.png")
            label = Gtk.Label(title)
            # button.connect("clicked", self._go_to_grid)
            button.get_style_context().add_class("middle")

        icon = Gtk.Image.new_from_file(icon_path)
        hbox.pack_start(icon, False, False, 0)
        hbox.pack_start(label, False, False, 0)

    attach_cursor_events(button)
    button.add(hbox)
    return button
