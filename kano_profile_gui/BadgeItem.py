#!/usr/bin/env python

# BadgeItem.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen

# import os
from gi.repository import Gtk, GdkPixbuf
import kano_profile_gui.components.icons as icons
import kano.gtk3.cursor as cursor
# from kano_profile_gui.paths import media_dir
from kano_profile_gui.image_helper_functions import (
    create_translucent_layer, get_image_path_at_size
)
import unicodedata


class BadgeItem(Gtk.Button):
    def __init__(self, badge_info):

        Gtk.Button.__init__(self)

        self.badge_info = badge_info
        self.title = badge_info["title"]
        self.unlocked_description = badge_info["desc_unlocked"]
        self.locked_description = badge_info["desc_locked"]
        background_color = badge_info['bg_color']
        self.locked = not badge_info['achieved']

        # This is the dimensions of the actual item
        self.width = 243
        self.height = 194

        # Dimensions of the image
        self.img_width = 230
        self.img_height = 180

        # Dimensions of the hover over label.
        self.label_height = 44

        self.get_style_context().add_class("badge_item")
        self.background_color = unicodedata.normalize(
            'NFKD', '#' + background_color
        ).encode('ascii', 'ignore')

        self.locked_background_color = '#e7e7e7'

        self.create_hover_box()

        self.set_size_request(self.width, self.height)
        self.connect("enter-notify-event", self.add_hover_style,
                     self.hover_box)
        self.connect("leave-notify-event", self.remove_hover_style,
                     self.hover_box)

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        self.fixed.set_size_request(self.width, self.height)
        self.pack_image(self.badge_info)

        cursor.attach_cursor_events(self)
        self.change_locked_style()

    def create_hover_box(self):
        self.hover_box = Gtk.EventBox()
        self.hover_box.get_style_context().add_class("hover_box")
        self.hover_label = Gtk.Label(self.get_title())
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_box.add(self.hover_label)
        self.hover_box.set_size_request(self.width, self.label_height)

    # This function contains the styling applied to the picture when the mouse
    # hovers over it.
    def add_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.fixed.put(self.hover_box, 0, self.height - self.label_height)
        self.show_all()

    def remove_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.fixed.remove(self.hover_box)

    def get_filename_at_size(self, width_of_image, height_of_image):
        return self.item.get_filename_at_size(width_of_image, height_of_image)

    def get_title(self):
        return self.title.upper()

    def pack_image(self, badge_info):
        '''
        Get the file path for the badge, pack it and optionally add
        an overlay.
        '''

        locked = not badge_info['achieved']
        force_locked = False

        img = Gtk.Image()

        # New system
        if 'image' in badge_info:
            path = badge_info['image']

            if locked:
                force_locked = True

            width = 130
            height = 130
            self.fixed.put(img, 60, 30)

        # Old system
        else:
            category = badge_info['category']
            name = badge_info['name']
            width = self.img_width
            height = self.img_height
            path = get_image_path_at_size(
                category, name, width, height, locked
            )
            self.fixed.put(img, 7, 7)

        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(path, width, height)
        img.set_from_pixbuf(pb)

        if force_locked:
            translucent_layer = create_translucent_layer(
                self.img_width, self.img_height
            )
            self.fixed.put(translucent_layer, 0, 0)

        return path

    def change_locked_style(self):
        if self.locked:
            self.padlock = icons.set_from_name("padlock")
            self.fixed.put(self.padlock, 100, 77)
            background_color = self.locked_background_color
        else:
            background_color = self.background_color

        style_provider = Gtk.CssProvider()
        css = ".badge_background {background: %s}" % background_color
        style_provider.load_from_data(css)

        style_context = self.get_style_context()
        style_context.add_class("badge_background")

        style_context.add_provider(
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )
