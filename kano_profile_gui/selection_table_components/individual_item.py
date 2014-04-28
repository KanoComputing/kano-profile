#!/usr/bin/env python

# indivdual_item.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk, GdkPixbuf, Gdk
from kano_profile_gui.images import get_image
import kano_profile_gui.components.constants as constants


class Picture():
    def __init__(self, info):
        # info is a dictionary containing item and group which we use to find filename, heading, description, colour of background

        self.width = 230
        self.height = 180
        self.label_height = 44
        self.category = info["category"]
        self.subcategory = info["subcategory"]
        self.badge = info["badge_name"]
        self.subcategory = info["subcategory"]
        self.locked = not info["unlocked"]
        bg_color = '#' + str(info["bg_color"])
        self.bg_color = Gdk.RGBA()
        self.bg_color.parse(bg_color)

        # split info into members
        self.title = info["title"]
        self.locked_description = info["locked_description"]
        self.unlocked_description = info["unlocked_description"]

        self.image = self.set_image_height()

        self.hover_box = Gtk.EventBox()
        self.hover_box.get_style_context().add_class("hover_box")
        self.hover_box.set_visible_window(False)
        self.hover_label = Gtk.Label(self.title)
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_box.add(self.hover_label)
        self.hover_box.set_size_request(self.width, self.label_height)

        self.button = Gtk.EventBox()
        self.button.set_size_request(self.width, self.height)
        self.button.connect("enter-notify-event", self.add_hover_style, self.hover_box)
        self.button.connect("leave-notify-event", self.remove_hover_style, self.hover_box)
        self.button.override_background_color(Gtk.StateFlags.NORMAL, self.bg_color)

        self.locked_box = Gtk.EventBox()
        self.locked_box.get_style_context().add_class("locked_box")
        self.locked_box.set_size_request(self.width, self.height)
        self.padlock = Gtk.Image()
        self.padlock.set_from_file(constants.media + "/images/icons/Level-4.png")
        self.locked_fixed = Gtk.Fixed()
        self.locked_fixed.put(self.locked_box, 0, 0)
        self.locked_fixed.put(self.padlock, 80, 55)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.width, self.height)

        self.fixed.put(self.hover_box, 0, self.height - self.label_height)
        if self.category == "environments":
            self.fixed.put(self.image, 0, 0)
        else:
            self.fixed.put(self.image, (self.width - self.height) / 2, 0)
        self.fixed.put(self.locked_fixed, 0, 0)

        self.button.add(self.fixed)

        # No item can be equipped (see extension of this class to equip items)
        self.equipable = False

        # We're not in the item's info screen
        self.selected = False

        self.set_locked(self.locked)

    # Sets whether the picture has a padlock in front or not.
    # locked = True or False
    def set_locked(self, locked):
        self.locked = locked
        if self.locked:
            self.add_locked_style()
        else:
            self.remove_locked_style()

    def get_locked(self):
        return self.locked

    def add_locked_style(self):
        self.locked_box.set_visible_window(True)
        self.padlock.set_visible(True)

    def remove_locked_style(self):
        #self.fixed.remove(self.locked_fixed)
        self.locked_box.set_visible_window(False)
        self.padlock.set_visible(False)

    # Sets whether the picture is selected, ie whether we are in the selection screen
    # selected = True or False
    def set_selected(self, selected):
        self.selected = selected

    def get_selected(self):
        return self.selected

    # This function contains the styling applied to the picture when the mouse hovers over it.
    def add_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.hover_box.set_visible_window(True)
        self.hover_label.set_visible(True)

    def remove_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.hover_box.set_visible_window(False)
        self.hover_label.set_visible(False)

    def get_filename_at_height(self, height_of_image):
        return get_image(self.category, self.subcategory, self.badge, height_of_image)

    def set_image_height(self):
        #filename = self.get_filename_at_height(height_of_image)
        pixbuf = self.set_pixbuf_height()
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def set_pixbuf_height(self):
        filename = self.get_filename_at_height(self.height)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        if self.category == "environments":
            pixbuf = pixbuf.new_subpixbuf(46, 0, self.width, self.height)
        else:
            pixbuf = pixbuf.new_subpixbuf(0, 0, self.height, self.height)
        return pixbuf

    def get_description(self):
        if self.locked:
            return self.locked_description
        else:
            return self.unlocked_description
