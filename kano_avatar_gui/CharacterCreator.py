#!/usr/bin/env python

# CharacterCreator.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano_avatar.logic import AvatarCreator, get_avatar_conf
from kano_avatar_gui.Menu import Menu
from kano_avatar_gui.ImageView import ImageView
from kano.logging import logger


# We make the inheritance from Gtk.EventBox so we can grab the events
class CharacterCreator(Gtk.EventBox):
    configuration = get_avatar_conf()
    avatar_cr = AvatarCreator(configuration)

    def __init__(self, randomise=False):
        Gtk.EventBox.__init__(self)

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)

        self._get_obj_data()

        if randomise:
            # Create random button
            random_button = self._create_random_button()
            self.fixed.put(random_button, 600, 0)

        # Check profile information and load up either the created avatar or
        # the default

        # read file, and if no record, show default
        self._set_defaults()

        self._create_img_box('avatar.png')
        self._create_menu()

        self.width = self._imgbox.width
        self.height = self._imgbox.height
        self.set_size_request(self.width, self.height)

        self.fixed.put(self._imgbox, 0, 0)
        self.fixed.put(self._menu, 30, 30)

        self.connect("button-release-event", self._hide_pop_ups)

    def get_image_path(self):
        containing_dir = os.path.join(os.path.expanduser('~'), "avatar-content")
        if not os.path.exists(containing_dir):
            os.mkdir(containing_dir)
        return os.path.join(containing_dir, "avatar.png")

    def _create_random_button(self):
        random_button = Gtk.Button()
        width = 60
        height = 60

        # TODO: get file path for the random icon
        icon = Gtk.Image()
        random_button.add(icon)
        random_button.get_style_context().add_class("random_button")
        random_button.set_size_request(width, height)
        random_button.connect("clicked", self._randomise_avatar_wrapper)

        return random_button

    def _randomise_avatar_wrapper(self, button):
        self.avatar_cr.randomise_all_items()
        self.avatar_cr.create_avatar('avatar.png')
        self.show_all()

    def _hide_pop_ups(self, widget, event):
        self._menu.hide_pop_ups()
        self._menu.unselect_categories()

    def _set_defaults(self):
        '''Set the default selection of the avatar creator.
        This should look like the Kano Judoka.
        '''
        # To select the defaults, you need to both pick them and create
        # a default image, and also select them in the category.
        # The second is less of a priority.

        # if the user has created one, that should be the default shown.
        # So maybe show the one that currently exists?
        # TODO Un hardcode the following
        self.avatar_cr.char_select('Judoka_Base')
        self.avatar_cr.obj_select(
            [
                'Skin_Orange',
                'Suit_White',
                'Face_Happy',
                'Hair_Black',
                'Belt_Orange',
                'Sticker_Code'
            ]
        )
        self.avatar_cr.create_avatar(save_to='avatar.png')

    def _create_menu(self):
        self._menu = Menu(self.avatar_cr)
        self._menu.connect('asset_selected', self._update_img)

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

    # Public function so external buttons can access it.
    def save(self):
        '''When saving character, we save all the images in kano-profile
        and move the img filename to a place we can share it from.
        '''

        saved_path = self.get_image_path()
        logger.debug("Saving generated avatar image to {}".format(saved_path))
        # Save the image as hard copy somewhere safe, store it,
        # and also lists which assets in kano-profile
        self.avatar_cr.save_image(saved_path)

        logger.debug("Saving all kano assets")

        # for all categories, check the item that was selected
        categories = self.avatar_cr.list_available_categories()

        for category in categories:
            # TODO
            pass
