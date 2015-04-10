#!/usr/bin/env python

# indivdual_item.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk, GdkPixbuf
import kano_profile_gui.components.icons as icons
import kano_profile_gui.components.cursor as cursor


class BadgeItem():
    def __init__(self, image_path, title, description, background_colour,
                 locked):

        self.width = 230
        self.height = 180
        self.label_height = 44
        # self.item = item

        self.image_path = image_path
        self.background_colour = background_colour
        self.title = title
        self.locked = locked

        self.image = Gtk.Image()

        self.hover_box = Gtk.EventBox()
        self.hover_box.get_style_context().add_class("hover_box")
        self.hover_box.set_visible_window(False)
        self.hover_label = Gtk.Label(self.get_title())
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_box.add(self.hover_label)
        self.hover_box.set_size_request(self.width, self.label_height)

        self.button = Gtk.EventBox()
        self.button.set_size_request(self.width, self.height)
        self.button.connect("enter-notify-event", self.add_hover_style,
                            self.hover_box)
        self.button.connect("leave-notify-event", self.remove_hover_style,
                            self.hover_box)
        self.button.override_background_color(Gtk.StateFlags.NORMAL,
                                              self.background_colour)

        self.padlock = icons.set_from_name("padlock")
        self.locked_fixed = Gtk.Fixed()
        self.locked_fixed.put(self.padlock, 95, 70)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.width, self.height)
        self.fixed.put(self.hover_box, 0, self.height - self.label_height)

        # The image can be smaller than the square in which case we
        # center it in the view.
        pb = self.image.get_pixbuf()
        img_width = pb.get_width()
        img_height = pb.get_height()
        self.fixed.put(self.image, (self.width - img_width) / 2,
                       (self.height - img_height) / 2)

        self.fixed.put(self.locked_fixed, 0, 0)

        self.button.add(self.fixed)
        cursor.attach_cursor_events(self.button)

        if self.item.equipable:
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
            self.equipped_box2.set_size_request(80, 25)

            # Border box of equipped style
            self.equipped_border = Gtk.EventBox()
            self.equipped_border.get_style_context().add_class("equipped_border")
            self.equipped_border.set_size_request(88, 33)

            self.fixed.put(self.equipped_box, 0, self.height - self.label_height)
            self.fixed.put(self.equipped_border, 10, 10)
            self.fixed.put(self.equipped_box2, 14, 14)

    # Sets whether the picture has a padlock in front or not.
    # locked = True or False
    def set_locked(self, locked):
        self.change_locked_style()

    def get_locked(self):
        return self.locked
        # return self.item.get_locked()

    def change_locked_style(self):
        self.padlock.set_visible(self.get_locked())
        self.button.override_background_color(Gtk.StateFlags.NORMAL, self.background_color)
        # self.button.override_background_color(Gtk.StateFlags.NORMAL, self.item.get_color())

    # This function contains the styling applied to the picture when the mouse
    # hovers over it.
    def add_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.hover_box.set_visible_window(True)
        self.hover_label.set_visible(True)

    def remove_hover_style(self, arg1=None, arg2=None, hover_box=None):
        self.hover_box.set_visible_window(False)
        self.hover_label.set_visible(False)

    def get_filename_at_size(self, width_of_image, height_of_image):
        return self.item.get_filename_at_size(width_of_image, height_of_image)

    def get_image_at_size(self):
        filename = self.get_filename_at_size(self.width, self.height)

        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, self.width,
                                                    self.height)
        self.image.set_from_pixbuf(pb)

    def get_title(self):
        return self.title.upper()

    def get_description(self):
        return self.description
