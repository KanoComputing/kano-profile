#!/usr/bin/env python

# CategoryMenu.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from gi.repository import Gtk, GObject
from kano_avatar_gui.SelectMenu import SelectMenu
from kano.gtk3.cursor import attach_cursor_events


class CategoryMenu(SelectMenu):

    __gsignals__ = {
        'category_item_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, parser):

        # for some reason, this is not being obeyed
        self.item_width = 55
        self.item_height = 50

        self._signal_name = 'category_item_selected'
        self._parser = parser

        # Initialise self._items
        self._items = {}

        # Save the order of the categories so we can use it outside
        self.categories = self._parser.list_available_categories()
        SelectMenu.__init__(self, self.categories, self._signal_name)

        # The menu is one item by 7 items
        self.set_size_request(self.item_width, 7 * self.item_height)
        self._pack_buttons()

    def _add_selected_appearence(self, identifier):
        '''Change the appearence to the button to one that appears to be
        selected.
        '''
        button = self._items[identifier]['button']
        self._add_selected_css(button)
        self._add_selected_image(button, identifier)

    def _remove_selected_appearence(self, identifier):
        '''If the identifier is not selected, remove the styling on it.
        '''
        button = self._items[identifier]['button']

        if identifier != self.get_selected():
            self._remove_selected_css(button)
            self._remove_selected_image(button, identifier)

    def _add_selected_appearence_wrapper(self, button, event, identifier):
        '''Wrapper of the _add_selected_appearence for the enter-notify-event
        on buttons.
        '''
        self._add_selected_appearence(identifier)

    def _remove_selected_appearence_wrapper(self, button, event, identifier):
        '''Wrapper of the _remove_selected_appearence for the
        leave-notify-event on buttons.
        '''
        self._remove_selected_appearence(identifier)

    def remove_selected_on_all(self):
        '''Remove the selected appearence on all the category buttons.
        '''
        self.set_selected(None)
        for cat in self.categories:
            self._remove_selected_appearence(cat)

    def _pack_buttons(self):
        '''Pack the buttons into the menu.
        '''
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        for category in self.categories:
            button = self._create_button(category)
            self.set_button(category, button)

            inactive_icon_path = self._parser.get_inactive_category_icon(
                category)
            self._add_option_to_items(category,
                                      'inactive_path',
                                      inactive_icon_path)
            active_icon_path = self._parser.get_active_category_icon(category)
            self._add_option_to_items(category,
                                      'active_path',
                                      active_icon_path)

            vbox.pack_start(button, True, True, 0)

    def _remove_button(self, identifier):
        ''' Reverse of _pack_buttons
        '''
        # TODO this is probably not the best way of getting the vbox
        vbox = self.get_children()[0]
        button = self.get_button(identifier)
        if button:
            vbox.remove(button)
            self.unset_button(identifier)
            self._remove_option_from_items(identifier, 'inactive_path')
            self._remove_option_from_items(identifier, 'active_path')
            button.destroy()

    def _select_button_wrapper(self, widget, identifier):
        '''This is connected to the button-release-event when you click on a
        button in the table.
        If the image is unlocked, add the css selected class, select the image
        and emit a signal that the parent window can use
        '''
        self.select_button(identifier)

    def select_button(self, identifier):
        '''This applies the selected appearence to the button associated with
        the identifier, sets it as selected and emits the signal.
        This is called outside the class on initialising the character
        creator in the registration screen, hence why is not a private
        function.
        '''
        self.set_selected(identifier)
        self.only_style_selected(identifier)

        # When an image is selected, emit a signal giving the
        # idenitifer as information
        self.emit(self._signal_name, identifier)

    def _create_button(self, identifier):
        '''Create a button with the styling needed for this
        widget.
        We can either pass the dictionary for the whole item,
        or feed in the individual arguments
        '''

        button = Gtk.Button()
        button.set_size_request(self.item_width, self.item_height)

        path = self._parser.get_inactive_category_icon(identifier)
        icon = Gtk.Image.new_from_file(path)
        button.add(icon)
        attach_cursor_events(button)

        button.get_style_context().add_class("category_item")
        button.connect("clicked", self._select_button_wrapper,
                       identifier)

        # Replace the grey icon with an orange on when the pointer
        # hovers over the button
        button.connect("enter-notify-event",
                       self._add_selected_appearence_wrapper,
                       identifier)
        button.connect("leave-notify-event",
                       self._remove_selected_appearence_wrapper,
                       identifier)
        return button

    def only_style_selected(self, identifier):
        '''Adds the CSS class that shows the image that has been selected,
        even when the mouse is moved away.
        If identifier is None, will remove all styling
        '''

        for name, img_dict in self._items.iteritems():
            if 'button' in img_dict:
                button = img_dict['button']
                self._remove_selected_css(button)
                self._remove_selected_image(button, name)

        if identifier in self._items:
            if 'button' in self._items[identifier]:
                button = self.get_button(identifier)
                self._add_selected_css(button)
                self._add_selected_image(button, identifier)

    def disable_all_buttons(self):
        '''Disable all the category buttons so when we're saving the
        character, the user doesn't press any other buttons.
        '''
        for category in self.categories:
            button = self.get_button(category)
            button.set_sensitive(False)

    def enable_all_buttons(self):
        '''Disable all the category buttons so when we're saving the
        character, the user doesn't press any other buttons.
        '''
        for category in self.categories:
            button = self.get_button(category)
            button.set_sensitive(True)
