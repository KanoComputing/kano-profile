#!/usr/bin/env python

# BadgeItem.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen

from gi.repository import Gtk, GdkPixbuf, Gdk
import kano_profile_gui.components.icons as icons
import kano.gtk3.cursor as cursor


class BadgeItem(Gtk.Button):

    def __init__(self, image, title, unlocked_description,
                 locked_description, background_color,
                 locked):

        Gtk.Button.__init__(self)

        # This is the dimensions of the actual item
        self.width = 243
        self.height = 194

        # Dimensions of the image
        self.img_width = 230
        self.img_height = 180

        # Dimensions of the hover over label.
        self.label_height = 44

        self.get_style_context().add_class("badge_item")

        self.unlocked_description = unlocked_description
        self.locked_description = locked_description
        self.title = title
        self.locked = locked

        self.background_color = Gdk.RGBA()
        self.background_color.parse('#' + background_color)

        self.locked_background_color = Gdk.RGBA()
        self.locked_background_color.parse('#e7e7e7')

        self.image = image
        self.create_hover_box()

        self.set_size_request(self.width, self.height)
        self.connect("enter-notify-event", self.add_hover_style,
                     self.hover_box)
        self.connect("leave-notify-event", self.remove_hover_style,
                     self.hover_box)

        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        self.fixed.set_size_request(self.width, self.height)
        self.fixed.put(self.image, 7, 7)

        cursor.attach_cursor_events(self)
        self.change_locked_style()

    def create_hover_box(self):
        self.hover_box = Gtk.EventBox()
        self.hover_box.get_style_context().add_class("hover_box")
        self.hover_label = Gtk.Label(self.get_title())
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_box.add(self.hover_label)
        self.hover_box.set_size_request(self.width, self.label_height)

    def get_locked(self):
        return self.locked

    def change_locked_style(self):
        if self.locked:
            self.padlock = icons.set_from_name("padlock")
            self.fixed.put(self.padlock, 100, 77)
            self.override_background_color(Gtk.StateFlags.NORMAL,
                                           self.locked_background_color)
        else:
            self.override_background_color(Gtk.StateFlags.NORMAL,
                                           self.background_color)

    # This function contains the styling applied to the picture when the mouse
    # hovers over it.
    def add_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.fixed.put(self.hover_box, 0, self.height - self.label_height)
        self.show_all()

    def remove_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.fixed.remove(self.hover_box)

    def get_filename_at_size(self, width_of_image, height_of_image):
        return self.item.get_filename_at_size(width_of_image, height_of_image)

    def get_image_at_size(self):
        filename = self.get_filename_at_size(self.width, self.height)

        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, self.width,
                                                    self.height)
        self.image.set_from_pixbuf(pb)

    def get_title(self):
        return self.title.upper()
