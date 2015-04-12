#!/usr/bin/env python

# Menu.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
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
from kano_profile.apps import load_app_state_variable, save_app_state_variable


class Menu(Gtk.Fixed):

    __gsignals__ = {
        'asset_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        # Could add this if environment became a special case
        'environment_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, parser):
        Gtk.Fixed.__init__(self)

        self._parser = parser
        self._cat_menu = CategoryMenu(self._parser)
        self._cat_menu.connect('category_item_selected',
                               self.launch_pop_up_menu)

        self.cat_position_x = 0
        self.cat_position_y = 0
        self.pop_up_pos_x = self.cat_position_x + self._cat_menu.item_width + 5
        self.pop_up_pos_y = self.cat_position_y

        self.put(self._cat_menu, 0, 0)

        # initialises self.menus
        self._initialise_pop_up_menus()
        self._create_start_up_image()

        self.show_all()

    def unselect_categories(self):
        self._cat_menu.remove_selected_on_all()

    def get_selected_category(self):
        return self._cat_menu.get_selected()

    def get_selected_obj(self, category):
        if "menu" in self.menus[category]:
            return self.menus[category]["menu"].get_selected()
        else:
            return ""

    def get_all_selected_objs(self):
        objs = []
        for category in self._cat_menu.categories:
            selected_obj = self.get_selected_obj(category)
            if selected_obj:
                objs.append(selected_obj)

        return objs

    def _initialise_pop_up_menus(self):
        '''Initialise the pop up menus
        '''
        logger.debug("Initialising PopUpMenu for all categories")
        self.menus = {}

        for category in self._cat_menu.categories:
            menu = PopUpItemMenu(category, self._parser)
            menu.connect('pop_up_item_selected', self._emit_signal)

            self.menus[category] = {}
            self.menus[category]["menu"] = menu

            self.put(self.menus[category]['menu'],
                     self.pop_up_pos_x, self.pop_up_pos_y)
            self.menus[category]['menu'].hide()

    def _create_start_up_image(self):
        '''We check what has been saved on kano-profile, and we use a default if
        something hasn't been specified
        '''
        logger.debug("Creating start up image")

        # TODO: fix this. This is only here to make this work.
        self._parser.char_select('Judoka_Base')

        categories = ['Belts', "Faces", "Hair", "Skins", "Stickers", "Suits"]
        defaults = {
            "Belts": 'Belt_Orange',
            'Suits': 'Suit_White',
            'Faces': 'Face_Happy',
            'Hair': 'Hair_Black',
            'Stickers': 'Sticker_Code',
            'Skins': 'Skin_Orange'
        }

        for category in categories:
            available_objects = self._parser.get_avail_objs(category)
            logger.debug("available_objects = {}".format(available_objects))

            obj_name = load_app_state_variable("kano-avatar", category)
            logger.debug("loading obj_name = {}".format(obj_name))

            if obj_name and obj_name in self._parser.get_avail_objs(category):
                logger.debug("Loading saved object {} for category {}".format(obj_name, category))
            else:
                obj_name = defaults[category]
                logger.debug("Loading default object {} for category {}".format(obj_name, category))
                save_app_state_variable("kano-avatar", category, obj_name)

            # object_list.append(obj_name)
            self.menus[category]["menu"]._set_selected(obj_name)
            self.menus[category]["menu"]._only_style_selected(obj_name)
            self.menus[category]["menu"].hide()
            logger.debug("Hid menu for category {}".format(category))

        # self._parser.obj_select(object_list)
        # self._parser.create_avatar(save_to='avatar.png')

    def launch_pop_up_menu(self, widget, category):

        logger.debug("Launching PopUpMenu for category {}".format(category))
        self.hide_pop_ups()
        self.menus[category]['menu'].show()

    def hide_pop_ups(self):
        for category, menu_dict in self.menus.iteritems():

            if "menu" in self.menus[category]:
                self.menus[category]["menu"].hide()

    def _emit_signal(self, widget, category):
        '''This is to propagate the signal the signal up a widget
        '''
        self.emit('asset_selected', category)
