#!/usr/bin/env python

# CharacterCreator.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk
from kano_avatar.logic import AvatarCreator, get_avatar_conf
from kano_avatar_gui.Menu import Menu
from kano_avatar_gui.ImageView import ImageView
from kano.logging import logger


class CharacterCreator(Gtk.Fixed):
    configuration = get_avatar_conf()
    avatar_cr = AvatarCreator(configuration)

    def __init__(self):
        Gtk.Fixed.__init__(self)

        self._get_obj_data()

        # TODO Un hardcode the following
        self.avatar_cr.char_select('Judoka_Base')

        self._create_img_box(self.avatar_cr.selected_char_asset())
        self._create_menu()

        self.width = self._imgbox.width
        self.height = self._imgbox.height
        self.set_size_request(self.width, self.height)

        self.put(self._imgbox, 0, 0)
        self.put(self._menu, 30, 30)

        self.show_all()

    def _create_menu(self):
        self._menu = Menu(self.avatar_cr)
        self._menu.connect('asset_selected', self._update_img)
        # self._grid.attach(self._menu, 0, 1, 1, 1)

    def _get_obj_data(self):
        self._list_of_categories = self.avatar_cr.list_available_categories()

    def _create_img_box(self, img_name):
        self._imgbox = ImageView(self)
        self._imgbox.set_image(img_name)

    def _update_img(self, widget, selected):
        list_of_objs = self._menu.get_all_selected_objs()
        rc = self.avatar_cr.obj_select(list_of_objs)
        if not rc:
            logger.error('Error processing the list {}'.format(list_of_objs))
        else:
            self.avatar_cr.create_avatar(save_to='avatar.png')
            self._imgbox.set_image('avatar.png')
