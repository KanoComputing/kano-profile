#!/usr/bin/env python

# item_selection_grid.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

from gi.repository import Gtk, GObject
import kano_profile_gui.components.icons as icons
from kano_profile_gui.components.cursor import attach_cursor_events
from kano_profile.badges import calculate_badges


class ItemSelectionGrid(Gtk.Grid):

    def __init__(self):
        Gtk.Grid.__init__(self)


class ItemButton(Gtk.Button):
    __gsignals__ = {
        'item-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, name, img_path, background_colour):
        Gtk.Button.__init__(self)
        self.name = name
        self.img_path = img_path
        self.background_colour = background_colour

    def emit_signal(self, widget):
        self.emit('item_button_selected', self.name)


class FullScreenItem(Gtk.EventBox):
    '''This has the full screen item, a button back to grid
    a next button and a previous button
    '''
    __gsignals__ = {
        'next-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'back-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, name, title, description):
        Gtk.EventBox.__init__(self)
        self.name = name
