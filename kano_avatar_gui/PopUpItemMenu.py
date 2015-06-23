#!/usr/bin/env python

# PopUpItemMenu.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from gi.repository import Gtk, GObject
from kano_avatar_gui.SelectMenu import SelectMenu
from kano.logging import logger
from kano.gtk3.cursor import attach_cursor_events
from kano.gtk3.scrolled_window import ScrolledWindow


class PopUpItemMenu(SelectMenu):
    '''This creates the pop out menu showing each of the items.
    '''

    __gsignals__ = {
        'pop_up_item_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, category, avatar_parser):
        logger.debug("Initialising pop up menu with category {}".format(category))

        self.top_bar_height = 50

        # Size of the selected icon
        self.button_width = 42
        self.button_height = 42

        self._category = category
        self._parser = avatar_parser
        self._signal_name = 'pop_up_item_selected'
        self._border_path = self._parser.get_selected_border(self._category)
        self._hover_path = self._parser.get_hover_border(self._category)

        obj_names = self._parser.list_avail_objs(self._category)
        SelectMenu.__init__(self, obj_names, self._signal_name)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Grid which the buttons are packed into
        self._grid = Gtk.Grid()

        # pack the grid into a sw of a specified height
        sw = ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.apply_styling_to_widget()
        sw.add(self._grid)
        sw.set_size_request(-1, 294)

        # Labels the category
        top_bar = self._create_top_bar()
        vbox.pack_start(top_bar, False, False, 0)
        vbox.pack_start(sw, False, False, 10)

        self._pack_items()
        self.show_all()

    ############################################################
    # UI functions

    def _create_top_bar(self):
        top_bar = Gtk.EventBox()
        top_bar.get_style_context().add_class("pop_up_menu_top_bar")
        label = Gtk.Label(self._category.title())
        label.set_alignment(0, 0.5)
        label.set_margin_left(20)
        top_bar.add(label)
        top_bar.set_size_request(-1, self.top_bar_height)
        return top_bar

    def _pack_items(self):
        '''Pack the buttons into the menu.
        '''

        # Assume the list of buttons are in self._buttons
        # Pack buttons into a grid

        # There are 2 columns
        total_columns = 2

        # These are the counters to keep track of where we are
        # in the grid.
        row = 0
        column = 0

        obj_names = self._parser.list_avail_objs(self._category)

        for name in obj_names:
            button = self._create_button(name)
            self._add_option_to_items(name, 'button', button)

            self._grid.attach(button, column, row, 1, 1)
            column += 1

            if column % total_columns == 0:
                row += 1
                column = 0

            # For now, we assume that none of the menus with
            # need more than 2 columns

        self._grid.set_margin_top(0)
        self._grid.set_margin_bottom(2)
        self._grid.set_margin_left(13)
        self._grid.set_margin_right(2)

    def _create_button(self, obj_name):
        '''This places the image onto a Gtk.Fixed so we can overlay a padlock
        on top (if the item is locked)
        This is then put onto a Gtk.Button with the appropriate CSS class.
        Returns the button.

        Hopefully this can be simplified with new assets
        '''

        # Create the container for the thumbnails
        fixed = Gtk.Fixed()

        path = self._parser.get_item_preview(obj_name)
        icon = Gtk.Image.new_from_file(path)

        # preview icon size (for all assets but the environment) is 41 by 41,
        # while the border is 42 by 42
        fixed.put(icon, 1, 1)

        button = Gtk.Button()
        button.get_style_context().add_class('pop_up_menu_item')
        button.add(fixed)

        # only attach the event listeners if the asset is unlocked
        if self._parser.is_unlocked(obj_name):
            button.connect('clicked', self._on_clicking_item, obj_name)
            button.connect('enter-notify-event',
                           self._add_hover_appearence_wrapper,
                           obj_name)
            button.connect('leave-notify-event',
                           self._remove_hover_appearence_wrapper,
                           obj_name)
            attach_cursor_events(button)

        button.set_size_request(self.button_width, self.button_height)

        # set a margin all the way around it
        button.set_margin_right(3)
        button.set_margin_left(3)
        button.set_margin_bottom(3)
        button.set_margin_top(3)

        return button

    ################################################################

    def _add_border(self, identifier, selected=True):
        '''Add the border image on top of the image
        It needs to be "above" as some of the border images also
        have a white tick.
        '''

        if identifier in self._items:
            button = self._items[identifier]['button']

            # Get the fixed containing the image
            fixed = button.get_child()

            if selected:
                # The border_path depends on the image.
                border = Gtk.Image.new_from_file(self._border_path)
                self._add_option_to_items(identifier, "selected_border",
                                          border)
                self._add_option_to_items(identifier, "selected_border_set",
                                          True)
            else:
                border = Gtk.Image.new_from_file(self._hover_path)
                self._add_option_to_items(identifier, "hover_border",
                                          border)
                self._add_option_to_items(identifier, "hover_border_set",
                                          True)

            # Put the selected border on the button
            fixed.put(border, 0, 0)
            fixed.show_all()

    def _remove_border(self, identifier, selected=True):
        '''If the icon in the menu has a selected border, this will remove
        the border.
        If identifier is None, all items will have the border removed
        '''
        if identifier in self._items:

            button = self._items[identifier]['button']
            fixed = button.get_children()[0]

            if selected and 'selected_border' in self._items[identifier]:

                # TODO: stop exposing self._items
                border = self._items[identifier]["selected_border"]
                self._add_option_to_items(identifier, "selected_border_set",
                                          False)
            elif not selected and 'hover_border' in self._items[identifier]:
                # TODO: stop exposing self._items
                border = self._items[identifier]["hover_border"]
                self._add_option_to_items(identifier, "hover_border_set",
                                          False)
            else:
                # Neither borders could be found
                return

            fixed.remove(border)
            button.show_all()

    def add_border_if_not_added(self, identifier, selected=True):
        '''Adds the selected styling if it is not already present
        '''
        if not self.get_if_styling_set(identifier, selected):
            self._add_border(identifier, selected)

    def remove_selected_border_if_not_selected(self, identifier):
        '''Adds the selected styling if the item is not selected
        '''
        if not (self.get_selected() == identifier) and \
                self.get_if_styling_set(identifier, selected=True):
            self._remove_border(identifier, selected=True)

    def get_if_styling_set(self, identifier, selected):
        '''Get if the styling has been applied to the item
        '''
        if selected:
            return (self.get_option(identifier, "selected_border_set") is True)
        else:
            return (self.get_option(identifier, "hover_border_set") is True)

    def only_style_selected(self, identifier):
        '''Adds the CSS class that shows the image that has been selected.
        If identifier is None, will remove selected styling.
        '''
        old_selected_id = self.get_selected()
        self.set_selected(identifier)

        if old_selected_id:
            self.remove_selected_border_if_not_selected(old_selected_id)

        # Since the item should already have the selected apearence from the
        # mouse hovering over it, should not bee needed to add the border again
        self.add_border_if_not_added(identifier, selected=True)

    #########################################################################
    # Wrapper functions, for callbacks

    def _add_hover_appearence_wrapper(self, button, event, identifier):
        self._add_border(identifier, selected=False)

    def _remove_hover_appearence_wrapper(self, button, event, identifier):
        '''For connecting to a button release event
        '''
        self._remove_border(identifier, selected=False)

    def _add_selected_appearence_wrapper(self, button, event, identifier):
        '''For connecting to a button release event
        '''
        self.add_border_if_not_added(identifier, selected=True)

    def _remove_selected_appearence_wrapper(self, button, event, identifier):
        '''For connecting to a button release event
        '''
        self.remove_selected_border_if_not_selected(identifier, selected=True)

    def _on_clicking_item(self, button, identifier):
        self.only_style_selected(identifier)
        self.emit(self._signal_name, identifier)
