#!/usr/bin/env python

# indivdual_item.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk  # , Gdk, GdkPixbuf
import kano_profile_gui.components.icons as icons


class IndividualItem():
    def __init__(self, item_group):
        # info is a dictionary containing item and group which we use to find filename, heading, description, colour of background

        self.width = 230
        self.height = 180
        self.label_height = 44
        self.items = item_group

        self.image = Gtk.Image()
        self.get_image_at_size()

        self.hover_box = Gtk.EventBox()
        self.hover_box.get_style_context().add_class("hover_box")
        self.hover_box.set_visible_window(False)
        self.hover_label = Gtk.Label(self.get_title())
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_box.add(self.hover_label)
        self.hover_box.set_size_request(self.width, self.label_height)

        self.button = Gtk.EventBox()
        self.button.set_size_request(self.width, self.height)
        self.button.connect("enter-notify-event", self.add_hover_style, self.hover_box)
        self.button.connect("leave-notify-event", self.remove_hover_style, self.hover_box)
        self.button.override_background_color(Gtk.StateFlags.NORMAL, self.get_visible().get_color())

        self.padlock = icons.set_from_name("padlock")
        self.locked_fixed = Gtk.Fixed()
        self.locked_fixed.put(self.padlock, 95, 70)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.width, self.height)
        self.fixed.put(self.hover_box, 0, self.height - self.label_height)
        self.fixed.put(self.image, 0, 0)
        self.fixed.put(self.locked_fixed, 0, 0)

        self.button.add(self.fixed)

        if self.get_visible().get_equipable():
             # Event box containing the time and title of the equipped item
            self.equipped_box = Gtk.EventBox()
            self.equipped_box.get_style_context().add_class("equipped_box")
            self.equipped_box.set_visible_window(False)
            self.equipped_label = Gtk.Label(self.get_title())
            self.equipped_box.add(self.equipped_label)
            self.equipped_box.set_size_request(self.width, self.label_height)

            # Event box containing the EQUIPPED label
            self.equipped_label2 = Gtk.Label("EQUIPPED")
            self.equipped_box2 = Gtk.EventBox()
            self.equipped_box2.get_style_context().add_class("equipped_box2")
            self.equipped_box2.add(self.equipped_label2)
            self.equipped_box2.set_size_request(90, 25)

            # Border box of equipped style
            self.equipped_border = Gtk.EventBox()
            self.equipped_border.get_style_context().add_class("equipped_border")
            self.equipped_border.set_size_request(98, 33)

            self.fixed.put(self.equipped_box, 0, self.height - self.label_height)
            self.fixed.put(self.equipped_border, 10, 10)
            self.fixed.put(self.equipped_box2, 14, 14)

    # Sets whether the picture has a padlock in front or not.
    # locked = True or False
    def set_locked(self, locked):
        self.change_locked_style()

    def get_locked(self):
        return self.get_visible().get_locked()

    def change_locked_style(self):
        self.padlock.set_visible(self.get_locked())
        self.button.override_background_color(Gtk.StateFlags.NORMAL, self.get_visible().get_color())

    # This function contains the styling applied to the picture when the mouse hovers over it.
    def add_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.hover_box.set_visible_window(True)
        self.hover_label.set_visible(True)

    def remove_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.hover_box.set_visible_window(False)
        self.hover_label.set_visible(False)

    def get_filename_at_size(self, width_of_image, height_of_image):
        return self.get_visible().get_filename_at_size(width_of_image, height_of_image)

    def get_image_at_size(self):
        filename = self.get_filename_at_size(self.width, self.height)
        self.image.set_from_file(filename)

    def get_title(self):
        return self.get_visible().title.upper()

    def get_description(self):
        return self.get_visible().get_description()

    def update_labels(self):
        self.hover_label.set_text(self.get_title())
        self.equipped_label.set_text(self.get_title())

    # Sets the visible picture to be equipped
    def set_equipped_item(self):
        item = self.get_visible()
        self.items.set_equipped_item(item)
        self.change_equipped_style()
        self.get_image_at_size()
        self.update_labels()

    def unequip_all(self):
        self.items.unequip_all()

    # Get the equipped item
    def get_equipped_item(self):
        return self.items.get_equipped()

    # Get whether the visible item is equipped
    def get_equipped(self):
        return self.get_visible().get_equipped()

    def set_visible(self, visible):
        self.items.set_visible(visible)
        self.get_image_at_size()
        self.image.show()

    def get_visible(self):
        return self.items.get_visible()

    # This function contains the styling applied to the picture when it is equipped.
    def change_equipped_style(self, arg1=None, arg2=None):
        self.equipped_box.set_visible_window(self.get_equipped())
        self.equipped_label.set_visible(self.get_equipped())
        self.equipped_box2.set_visible_window(self.get_equipped())
        self.equipped_label2.set_visible(self.get_equipped())
        self.equipped_border.set_visible_window(self.get_equipped())
        if not self.get_visible().equipped:
            self.hover_box.set_visible_window(False)
            self.hover_label.set_visible(False)
