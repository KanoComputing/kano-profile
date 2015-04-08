#!/usr/bin/env python

# Menu.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys
from gi.repository import Gtk, GObject

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)
        print dir_path

from kano_avatar_gui.PopUpItemMenu import PopUpItemMenu
from kano_avatar_gui.CategoryMenu import CategoryMenu


class Menu(Gtk.Fixed):

    __gsignals__ = {
        'asset_selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
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

        self.menus = {}

        for category in self._cat_menu.categories:
            self.menus[category] = {}

        self.show_all()

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

    def launch_pop_up_menu(self, widget, category):

        self._hide_menus()

        if "menu" not in self.menus[category]:
            menu = PopUpItemMenu(category, self._parser)
            menu.connect('pop_up_item_selected', self._emit_signal)

            self.menus[category]["menu"] = menu
            self.put(self.menus[category]['menu'],
                     self.pop_up_pos_x, self.pop_up_pos_y)

            self.menus[category]['menu'].show()
        else:
            self.menus[category]["menu"].show()

    def _hide_menus(self):
        for category, menu_dict in self.menus.iteritems():

            if "menu" in self.menus[category]:
                self.menus[category]["menu"].hide()

    def _emit_signal(self, widget, category):
        '''This is to propagate the signal the signal up a widget
        '''
        self.emit('asset_selected', category)
