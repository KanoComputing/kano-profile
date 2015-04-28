#!/usr/bin/env python

# CharacterCreator.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk
from kano_avatar.logic import AvatarCreator, get_avatar_conf
from kano_avatar.paths import AVATAR_DEFAULT_LOC, AVATAR_DEFAULT_NAME
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
    meny_y_pos = 20

    def __init__(self, randomise=False):
        Gtk.EventBox.__init__(self)

        # This is the avatar specific styling
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
        self.fixed.put(self._menu, 20, self.meny_y_pos)

        if randomise:
            # Create random button
            random_button = self._create_random_button()
            self.fixed.put(random_button, 645, self.meny_y_pos)

        self.connect("button-release-event", self._hide_pop_ups)
        self._update_img(None, None)

    def show_pop_up_menu_for_category(self, category):
        self._menu.launch_pop_up_menu(None, category)

    def get_image_path(self):
        img_path = self.avatar_cr.get_default_final_image_path()
        containing_dir = os.path.dirname(img_path)

        if not containing_dir:
            os.makekdirs(containing_dir)
        return img_path

    def update_from_saved_image(self):
        self._imgbox.set_image(self.get_image_path())

    def get_avatar_save_path(self):
        return os.path.abspath(
            os.path.expanduser(
                os.path.join(AVATAR_DEFAULT_LOC, AVATAR_DEFAULT_NAME)))

    def _create_random_button(self):
        random_button = Gtk.Button()
        width = 40
        height = 40

        # TODO: get file path for the random icon
        icon_path = os.path.join(media_dir, "images/icons/random.png")
        icon = Gtk.Image.new_from_file(icon_path)
        random_button.set_image(icon)
        random_button.get_style_context().add_class("random_button")
        random_button.set_size_request(width, height)
        random_button.connect("clicked", self._randomise_avatar_wrapper)
        random_button.connect("enter-notify-event", self._set_random_orange_icon)
        random_button.connect("leave-notify-event", self._set_random_grey_icon)
        attach_cursor_events(random_button)

        return random_button

    def _set_random_orange_icon(self, random_btn, event):
        icon_path = os.path.join(media_dir, "images/icons/random-active.png")
        icon = Gtk.Image.new_from_file(icon_path)
        random_btn.set_image(icon)

    def _set_random_grey_icon(self, random_btn, event):
        icon_path = os.path.join(media_dir, "images/icons/random.png")
        icon = Gtk.Image.new_from_file(icon_path)
        random_btn.set_image(icon)

    def _randomise_avatar_wrapper(self, button):
        logger.debug("\n_randomise_avatar_wrapper")
        self.randomise_avatar()

    def randomise_avatar(self):
        selected_item_dict = self.avatar_cr.randomise_all_items()
        filepath = self.avatar_cr.create_avatar()
        self._imgbox.set_image(filepath)
        self._menu.select_pop_up_items(selected_item_dict)

    def reset_selected_menu_items(self):
        self._menu.reset_selected_menu_items()

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
            displ_img = self.avatar_cr.create_avatar()
            self._imgbox.set_image(displ_img)

    # Public function so external buttons can access it.
    def save(self):
        '''When saving character, we save all the images in kano-profile
        and move the img filename to a place we can share it from.
        '''
        logger.debug("Saving data")

        saved_path = self.get_avatar_save_path()
        # Save the image as hard copy somewhere safe, store it,
        self.avatar_cr.save_final_assets(saved_path)
        logger.debug("Saving generated avatar image to {}".format(saved_path))

        logger.debug("Saving all kano assets")
        # and also lists which assets in kano-profile

        self._menu.saved_selected_list = {}

        # for all categories, check the item that was selected
        categories = self.avatar_cr.list_available_categories()

        for category in categories:
            obj_name = self._menu.get_selected_obj(category)
            save_app_state_variable('kano-avatar', category, obj_name)
            self._menu.saved_selected_list[category] = obj_name
