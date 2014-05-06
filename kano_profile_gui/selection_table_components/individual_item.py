#!/usr/bin/env python

# indivdual_item.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk, Gdk, GdkPixbuf
from kano_profile_gui.images import get_image
import kano_profile_gui.components.icons as icons


class IndividualItem():
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
        self.grey_bg = Gdk.RGBA()
        self.grey_bg.parse("#e7e7e7")

        # split info into members
        self.title = info["title"]
        self.locked_description = info["locked_description"]
        self.unlocked_description = info["unlocked_description"]

        self.image = self.get_image_at_size()

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
        self.padlock = icons.set_from_name("padlock")
        self.locked_fixed = Gtk.Fixed()
        self.locked_fixed.put(self.locked_box, 0, 0)
        self.locked_fixed.put(self.padlock, 95, 70)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.width, self.height)

        self.fixed.put(self.hover_box, 0, self.height - self.label_height)
        self.fixed.put(self.image, 0, 0)
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
        self.button.override_background_color(Gtk.StateFlags.NORMAL, self.grey_bg)

    def remove_locked_style(self):
        self.locked_box.set_visible_window(False)
        self.padlock.set_visible(False)
        self.button.override_background_color(Gtk.StateFlags.NORMAL, self.bg_color)

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

    def get_filename_at_size(self, width_of_image, height_of_image):
        return get_image(self.category, self.subcategory, self.badge, str(width_of_image) + "x" + str(height_of_image))

    def get_image_at_size(self):
        image = Gtk.Image()
        filename = self.get_filename_at_size(self.width, self.height)
        image.set_from_file(filename)
        return image

    def get_pixbuf_at_size(self):
        filename = self.get_filename_at_size(self.width, self.height)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        return pixbuf

    def get_description(self):
        if self.locked:
            return self.locked_description
        else:
            return self.unlocked_description
