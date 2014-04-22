#!/usr/bin/env python

# selection_picture.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk, GdkPixbuf
import kano_profile_gui.components.constants as constants


class Picture():
    def __init__(self, subfolder, picture_name, environment_info):

        self.dir = constants.media + "/" + subfolder + "/"
        self.filename = self.dir + picture_name + ".png"

        self.width = 230
        self.height = 180
        self.label_height = 44

        self.number_of_columns = 3
        self.number_of_rows = 3

        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.width, self.height)
        self.image = Gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)
        self.button = Gtk.EventBox()
        self.button.connect("button_press_event", self.toggle_selected)
        self.button.get_style_context().add_class("environment_background")
        self.button.set_size_request(self.width, self.height)

        self.enter_event = self.button.connect("enter-notify-event", self.add_hover_style)
        self.leave_event = self.button.connect("leave-notify-event", self.remove_hover_style)

        self.hover_label = Gtk.EventBox()
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_label.set_visible_window(False)
        self.hover_text = Gtk.Label(environment_info)
        self.hover_text.get_style_context().add_class("hover_text")
        self.hover_label.add(self.hover_text)
        self.hover_label.set_size_request(self.width, self.label_height)

        self.selected_label = Gtk.EventBox()
        self.selected_label.get_style_context().add_class("selected_label")
        self.selected_label.set_visible_window(False)
        self.selected_text = Gtk.Label(environment_info)
        self.selected_text.get_style_context().add_class("selected_text")
        self.selected_label.add(self.selected_text)
        self.selected_label.set_size_request(self.width, self.label_height)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.width, self.height)
        self.fixed.put(self.image, 0, 0)
        self.fixed.put(self.hover_label, 0, self.height - self.label_height)
        self.fixed.put(self.selected_label, 0, self.height - self.label_height)

        self.button.add(self.fixed)

        # Default, set locked to True and selected to False.
        self.locked = True
        self.selected = False

    # Sets whether the picture has a padlock in front or not.
    # locked = True or False
    def set_locked(self, locked):
        self.locked = locked

    def get_locked(self):
        return self.locked

    # Sets whether the picture is selected
    # selected = True or False
    def set_selected(self, selected):
        self.selected = selected

    def get_selected(self):
        return self.selected

    def toggle_selected(self, arg1=None, arg2=None):
        self.set_selected(not self.get_selected())

    # This function contains the styling applied to the picture when the mouse hovers over it.
    def add_hover_style(self, arg1=None, arg2=None):
        self.hover_label.set_visible_window(True)
        self.hover_text.set_visible(True)

    def remove_hover_style(self, arg1=None, arg2=None):
        self.hover_label.set_visible_window(False)
        self.hover_text.set_visible(False)

    # This function contains the styling applied to the picture when it is selected.
    def add_selected_style(self, arg1=None, arg2=None):
        self.selected_label.set_visible_window(True)
        self.selected_text.set_visible(True)

    def remove_selected_style(self, arg1=None, arg2=None):
        self.selected_label.set_visible_window(False)
        self.selected_text.set_visible(False)
        self.hover_label.set_visible_window(False)
        self.hover_text.set_visible(False)
