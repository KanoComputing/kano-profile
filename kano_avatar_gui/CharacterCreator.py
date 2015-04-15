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
from kano_profile.apps import save_app_state_variable
from kano_profile_gui.paths import media_dir
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano.gtk3.cursor import attach_cursor_events


# We make the inheritance from Gtk.EventBox so we can grab the events
class CharacterCreator(Gtk.EventBox):
    configuration = get_avatar_conf()
    avatar_cr = AvatarCreator(configuration)

    def __init__(self, randomise=False):
        Gtk.EventBox.__init__(self)

        # when called from kano-profile, we don't get this styling
        # otherwise
        css_path = os.path.join(media_dir, "CSS/avatar_generator.css")
        apply_styling_to_screen(css_path)

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        self._get_obj_data()

        # Check profile information and load up either the created avatar or
        # the default
        self._create_menu()
        self._create_img_box(self.get_image_path())

        self.width = self._imgbox.width
        self.height = self._imgbox.height
        self.set_size_request(self.width, self.height)

        self.fixed.put(self._imgbox, 0, 0)
        self.fixed.put(self._menu, 30, 30)

        if randomise:
            # Create random button
            random_button = self._create_random_button()
            self.fixed.put(random_button, 630, 30)

        self.connect("button-release-event", self._hide_pop_ups)
        self._update_img(None, None)

    def get_image_path(self, avatar_only=False):
        containing_dir = os.path.join(os.path.expanduser('~'), "avatar-content")
        if not os.path.exists(containing_dir):
            os.mkdir(containing_dir)
        if avatar_only:
            return os.path.join(containing_dir, "avatar.png")
        else:
            return os.path.join(containing_dir, "avatar_inc_env.png")

    def _create_random_button(self):
        random_button = Gtk.Button()
        width = 60
        height = 60

        # TODO: get file path for the random icon
        icon_path = os.path.join(media_dir, "images/icons/random.png")
        icon = Gtk.Image.new_from_file(icon_path)
        random_button.add(icon)
        random_button.get_style_context().add_class("random_button")
        random_button.set_size_request(width, height)
        random_button.connect("clicked", self._randomise_avatar_wrapper)
        attach_cursor_events(random_button)

        return random_button

    def _randomise_avatar_wrapper(self, button):
        self.avatar_cr.randomise_all_items()
        self.avatar_cr.create_avatar(self.get_image_path(avatar_only=True))
        self.show_all()
        self._hide_pop_ups()

    def _hide_pop_ups(self, widget=None, event=None):
        self._menu.hide_pop_ups()
        self._menu.unselect_categories()

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
            self.avatar_cr.create_avatar(self.get_image_path(avatar_only=True))
            self._imgbox.set_image(self.get_image_path())

    # Public function so external buttons can access it.
    def save(self):
        '''When saving character, we save all the images in kano-profile
        and move the img filename to a place we can share it from.
        '''
        logger.debug("Saving data")

        saved_path = self.get_image_path(avatar_only=True)
        logger.debug("Saving generated avatar image to {}".format(saved_path))
        # Save the image as hard copy somewhere safe, store it,
        # and also lists which assets in kano-profile
        self.avatar_cr.save_image(saved_path)

        logger.debug("Saving all kano assets")

        # for all categories, check the item that was selected
        categories = self.avatar_cr.list_available_categories()

        for category in categories:
            # TODO
            obj_name = self._menu.get_selected_obj(category)
            save_app_state_variable('kano-avatar', category, obj_name)
