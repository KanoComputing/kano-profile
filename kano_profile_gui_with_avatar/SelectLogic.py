#!/usr/bin/env python

# SelectMenu.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk


class SelectMenu(Gtk.EventBox):
    def __init__(self, list_of_names, signal_name):

        Gtk.EventBox.__init__(self)

        # Initialise self._items
        self._items = {}

        for name in list_of_names:
            self._items[name] = {}
            self._items[name]["selected"] = False

        self._signal_name = signal_name

        # This is the selected_identifier
        self._selected = None

    def _set_selected(self, identifier):
        '''Sets the selected element in the dictionary to True,
        and sets all the others to False
        '''

        self._selected = identifier

    def get_selected(self):
        '''Gets the name of the current selected image
        '''

        return self._selected

    def _unselect_all(self):
        '''Remove all styling on all images, and sets the 'selected'
        field to False
        '''
        self._selected = None

    def _add_option_to_items(self, identifier, name, item):
        '''Adds a new option in the self._items
        '''

        if identifier in self._items:
            self._items[identifier][name] = item

    def _add_selected_css(self, button):
        style = button.get_style_context()
        style.add_class("selected")

    def _remove_selected_css(self, button):
        style = button.get_style_context()
        style.remove_class("selected")

    def _add_selected_image(self, button, identifier):
        '''Pack the selected image into the button
        '''
        if 'unlocked' in self._items[identifier]:
            path = self._items[identifier]["locked"]
            image = Gtk.Image.new_from_file(path)
            button.set_image(image)

    def _remove_selected_image(self, button, identifier):
        '''Pack the grey unselected image into the button
        '''
        if 'locked' in self._items[identifier]:
            path = self._items[identifier]["locked"]
            image = Gtk.Image.new_from_file(path)
            button.set_image(image)
