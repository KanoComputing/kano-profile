#!/usr/bin/env python

# indivdual_item.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk, GdkPixbuf


class Picture():
    def __init__(self, info):
        # info is a dictionary containing name of picture file, heading, date, info about the item, hover over text shown

        self.filename = info["filename"]

        self.width = 230
        self.height = 180
        self.label_height = 44

        # split info into members
        self.heading = info["heading"]
        self.description = info["description"]

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.width, self.height)
        self.image = Gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
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
        self.fixed.put(self.image, 0, 0)
        self.fixed.put(self.hover_box, 0, self.height - self.label_height)

        self.button.add(self.fixed)

        # Default, set locked to True.
        self.locked = True

        # No item can be equipped
        self.equipable = False

    # Sets whether the picture has a padlock in front or not.
    # locked = True or False
    def set_locked(self, locked):
        self.locked = locked

    def get_locked(self):
        return self.locked

    # Sets whether the picture is selected, ie whether we should go to the selection screen
    # selected = True or False
    #def set_selected(self, selected):
    #    self.selected = selected

    #def get_selected(self):
    #    return self.selected

    # This function contains the styling applied to the picture when the mouse hovers over it.
    def add_hover_style(self, arg1=None, arg2=None):
        self.hover_box.set_visible_window(True)
        self.hover_label.set_visible(True)

    def remove_hover_style(self, arg1=None, arg2=None):
        self.hover_box.set_visible_window(False)
        self.hover_label.set_visible(False)
