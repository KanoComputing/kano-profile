#!/usr/bin/env python

# Menu.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import sys
from gi.repository import Gtk, GObject

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano_avatar_gui.PopUpItemMenu import PopUpItemMenu
from kano_avatar_gui.CategoryMenu import CategoryMenu
from kano.logging import logger
from kano_profile.profile import get_avatar, get_environment


class Menu(Gtk.Fixed):

    __gsignals__ = {
        'asset_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'randomise_all': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, parser, no_sync=False):
        Gtk.Fixed.__init__(self)

        self._parser = parser
        char, item = get_avatar(sync=not no_sync)
        self._parser.char_select(char)
        self._cat_menu = CategoryMenu(self._parser)
        self._cat_menu.connect('category_item_selected',
                               self.launch_pop_up_menu)
        self.categories = self._cat_menu.categories

        self.cat_position_x = 0
        self.cat_position_y = 0
        # Added an offset of 18 px to support the scrollbar category menu
        self.pop_up_pos_x = (self.cat_position_x + self._cat_menu.item_width +
                             5 + 18)
        self.pop_up_pos_y = self.cat_position_y
        self.put(self._cat_menu, 0, 0)

        self._initialise_pop_up_menus()
        self._create_start_up_image(char_item_tup=(char,item))
        self.show_all()

    def select_category_button(self, identifier):
        self._cat_menu.select_button(identifier)

    def unselect_categories(self):
        self._cat_menu.remove_selected_on_all()

    def get_selected_category(self):
        return self._cat_menu.get_selected()

    def get_selected_obj(self, category):
        if "pop_up" in self.menus[category]:
            return self.menus[category]["pop_up"].get_selected()
        else:
            return ""

    def get_all_selected_objs(self):
        objs = []
        for category in self._cat_menu.categories:
            selected_obj = self.get_selected_obj(category)
            if selected_obj:
                objs.append(selected_obj)

        return objs

    def _on_char_select(self, widget, char_id, randomise=True):
        if self._parser.selected_char() == char_id:
            return None
        self._remove_pop_up_menus()
        self._parser.char_select(char_id)
        self._cat_menu.set_new_categories()
        self._initialise_pop_up_menus()
        for cat in self.menus:
            if cat != self._parser.char_label:
                self.menus[cat]["pop_up"].hide()
        self.menus[self._parser.char_label]["pop_up"].show()
        self._cat_menu.show_all()
        if randomise:
            self.emit('randomise_all')

    def _initialise_pop_up_menus(self):
        self.menus = {}

        for category in self._cat_menu.categories:
            pop_up = PopUpItemMenu(category, self._parser)
            pop_up.connect('pop_up_item_selected', self._emit_signal)
            pop_up.connect('character_selected', self._on_char_select)

            self.menus[category] = {}
            self.menus[category]["pop_up"] = pop_up

            self.put(self.menus[category]['pop_up'],
                     self.pop_up_pos_x, self.pop_up_pos_y)

    def _remove_pop_up_menus(self):
        for category in self.menus:
            pop_up = self.menus[category]['pop_up']
            if pop_up:
                # TODO remove is redundant when using the destroy maybe?
                self.remove(pop_up)
                pop_up.destroy()

    def _create_start_up_image(self, char_item_tup=None, env=None):
        '''We check what has been saved on kano-profile, and we use a default if
        something hasn't been specified
        '''
        logger.debug("Creating start up image")

        # This is a dictionary so we can eaily reset the menus
        self.saved_selected_list = {}

        if char_item_tup is None:
            char, item = get_avatar()
        else:
            char, item = char_item_tup

        if env is None:
            env = get_environment()

        item[self._parser.char_label] = char
        item[self._parser.env_label] = env

        self._parser.char_select(char)

        for category in self._cat_menu.categories:
            # TODO this is temporary for the kano-content demo
            if category not in item:
                obj_name = None
            else:
                obj_name = item[category]
            logger.debug("loading obj_name = {}".format(obj_name))

            if obj_name and obj_name in self._parser.list_avail_objs(category):
                logger.debug(
                    "Loading saved object {} for category {}".format(
                        obj_name,
                        category)
                )
            else:
                logger.debug(
                    "Object {} for category {} not available".format(
                        obj_name,
                        category)
                )

            # object_list.append(obj_name)
            self.select_pop_up_in_category(category, obj_name)
            self.menus[category]["pop_up"].hide()
            self.saved_selected_list[category] = obj_name

    def select_pop_up_in_category(self, category, obj_name):
        self.menus[category]["pop_up"].set_selected(obj_name)
        self.menus[category]["pop_up"].only_style_selected(obj_name)

    def select_pop_up_items(self, selected_items):
        '''selected_items are of the form
        {category: {name: item_name}}
        '''

        for category, item_dict in selected_items.iteritems():
            pop_up = self.menus[category]["pop_up"]
            identifier = selected_items[category]
            pop_up.only_style_selected(identifier)

    def reset_selected_menu_items(self):
        saved_char = self.saved_selected_list[self._parser.char_label]
        if self._parser.selected_char() != saved_char:
            self._on_char_select(None, saved_char, randomise=False)
        self.select_pop_up_items(self.saved_selected_list)

    def launch_pop_up_menu(self, widget, category):
        '''Show the pop up menu for the correct category.
        This involves hiding all the pop up menus and then displaying the
        correct one.
        '''
        self.hide_pop_ups()
        self.menus[category]['pop_up'].show()

    def hide_pop_ups(self):
        for category, menu_dict in self.menus.iteritems():

            if "pop_up" in self.menus[category]:
                self.menus[category]["pop_up"].hide()

    def _emit_signal(self, widget, category):
        '''This is to propagate the signal the signal up a widget.
        '''
        self.emit('asset_selected', category)

    def disable_all_buttons(self):
        '''Disable all the category buttons so when we're saving the
        character, the user doesn't press any other buttons.
        '''
        self._cat_menu.disable_all_buttons()

    def enable_all_buttons(self):
        '''Enable all the category buttons.
        '''
        self._cat_menu.enable_all_buttons()
