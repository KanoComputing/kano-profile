#!/usr/bin/env python

# item_info.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This contains the info of each item, and getters and setters for all info

from kano_profile_gui.images import get_image
from gi.repository import Gdk


class ItemInfo():
    def __init__(self, info):
        # category = Badge, Avatar, Environment
        self.category = info["category"]
        # Parent folder of item.  E.g. online folder for badges.
        # In swag, this is important as all the images in the same parent folder will be only shown once on the selection table
        self.subcategory = info["subcategory"]
        # name of the image
        self.name = info["badge_name"]
        # name of the locked image
        self.locked_name = self.name + "_locked"
        # Whether the badge is locked or not
        self.locked = not info["unlocked"]
        # The unlocked background color
        bg_color = '#' + str(info["bg_color"])
        self.bg_color = Gdk.RGBA()
        self.bg_color.parse(bg_color)
        # The locked background color
        grey_bg = "#e7e7e7"
        self.grey_bg = Gdk.RGBA()
        self.grey_bg.parse(grey_bg)

        # title to show on the info screen
        self.title = info["title"]
        # Description to show on info screen is locked (e.g. how to unlock it)
        self.locked_description = info["locked_description"]
        # Description of the unlocked item
        self.unlocked_description = info["unlocked_description"]

        # If False, no item can be equipped
        # Badges are not equippable, swag is.
        # We can define this from the category
        if self.category == "badges":
            self.equipable = False
        else:
            self.equipable = True
            self.equipped = False

        # We're not in the item's info screen
        self.selected = False

        # If this item is visible, i.e. shown on table
        self.visible = False

    # Sets whether the picture is selected, ie whether we are in the selection screen
    # selected = True or False
    def set_selected(self, selected):
        self.selected = selected

    def get_selected(self):
        return self.selected

    # Sets whether we see the picture when on a table
    # visible = True or False
    def set_visible(self, visible):
        self.visible = visible

    def get_visible(self):
        return self.visible

    def get_description(self):
        if self.locked:
            return self.locked_description
        else:
            return self.unlocked_description

    # locked = True or False
    def set_locked(self, locked):
        self.locked = locked

    def get_locked(self):
        return self.locked

    def get_equipable(self):
        return self.equipable

    # Sets whether the item
    # equipped = True or False
    def set_equipped(self, equipped):
        if self.equipable:
            self.equipped = equipped

    def get_equipped(self):
        if self.equipable:
            if self.equipped is None:
                self.equipped = False
            return self.equipped

    # These functions get the current bacground color, name and description, depending on whether the
    # item is locked
    def get_color(self):
        if self.get_locked():
            return self.grey_bg
        else:
            return self.bg_color

    def get_decription(self):
        if self.get_locked():
            return self.locked_description
        else:
            return self.description

    def get_name(self):
        if self.get_locked():
            return self.locked_name
        else:
            return self.name

    def get_filename_at_size(self, width_of_image, height_of_image):
        return get_image(self.category, self.subcategory, self.get_name(), str(width_of_image) + "x" + str(height_of_image))
