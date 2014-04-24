#!/usr/bin/env python

# indivdual_item.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk
from kano_profile_gui.images import get_image


class Picture():
    def __init__(self, info):
        # info is a dictionary containing item and group which we use to find filename, heading, description, colour of background

        self.width = 230
        self.height = 180
        self.label_height = 44
        self.category = info["category"]
        self.item = info["item"]
        self.group = info["group"]

        # split info into members
        self.heading = info["heading"]
        self.description = info["description"]

        if self.category == "environments":
            self.image = self.set_image_width(self.width)
        else:
            self.image = self.set_image_width(self.height)

        self.button = Gtk.EventBox()
        self.button.set_size_request(self.width, self.height)

        self.enter_event = self.button.connect("enter-notify-event", self.add_hover_style)
        self.leave_event = self.button.connect("leave-notify-event", self.remove_hover_style)

        self.hover_box = Gtk.EventBox()
        self.hover_box.get_style_context().add_class("hover_box")
        self.hover_box.set_visible_window(False)
        self.hover_label = Gtk.Label(self.heading)
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_box.add(self.hover_label)
        self.hover_box.set_size_request(self.width, self.label_height)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.width, self.height)
        # TODO: in the case of badges, because the badge is square, we need to add (self.width-self.height)/2 padding to
        # the badge
        if self.category == "environments":
            self.fixed.put(self.image, 0, 0)
        else:
            self.fixed.put(self.image, (self.width - self.height) / 2, 0)
        self.fixed.put(self.hover_box, 0, self.height - self.label_height)

        self.button.add(self.fixed)

        # Default, set locked to True.
        self.locked = True

        # No item can be equipped
        self.equipable = False

        # We're not in the item's info screen
        self.selected = False

    # Sets whether the picture has a padlock in front or not.
    # locked = True or False
    def set_locked(self, locked):
        self.locked = locked

    def get_locked(self):
        return self.locked

    # Sets whether the picture is selected, ie whether we are in the selection screen
    # selected = True or False
    def set_selected(self, selected):
        self.selected = selected

    def get_selected(self):
        return self.selected

    # This function contains the styling applied to the picture when the mouse hovers over it.
    def add_hover_style(self, arg1=None, arg2=None):
        self.hover_box.set_visible_window(True)
        self.hover_label.set_visible(True)

    def remove_hover_style(self, arg1=None, arg2=None):
        self.hover_box.set_visible_window(False)
        self.hover_label.set_visible(False)

    def set_image_width(self, width_of_image):
        filename = get_image(self.item, self.group, width_of_image)
        image = Gtk.Image()
        image.set_from_file(filename)
        return image
