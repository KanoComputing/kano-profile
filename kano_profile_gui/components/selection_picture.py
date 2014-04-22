#!/usr/bin/env python

# selecttion_picture.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the size and styling of the pictures displayed on the table
# Used for badges, environments and avatar screen


from gi.repository import Gtk, GdkPixbuf
import kano_profile_gui.components.constants as constants


class Picture():
    def __init__(self, subfolder, info):
        # info is a dictionary containing name of picture file, heading, date, info about the item, hover over text shown

        self.dir = constants.media + "/" + subfolder + "/"
        self.filename = self.dir + info["name"] + ".png"

        self.width = 230
        self.height = 180
        self.label_height = 44

        # split info into members
        self.heading = info["heading"]
        self.date = info["date"]
        self.description = info["description"]
        self.hover_text = info["hover_over_info"]

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
        self.hover_label = Gtk.Label(self.hover_text)
        self.hover_label.get_style_context().add_class("hover_label")
        self.hover_box.add(self.hover_label)
        self.hover_box.set_size_request(self.width, self.label_height)

        self.equipped_box = Gtk.EventBox()
        self.equipped_box.get_style_context().add_class("equipped_box")
        self.equipped_box.set_visible_window(False)
        self.equipped_label = Gtk.Label(self.hover_text)
        self.equipped_label.get_style_context().add_class("equipped_label")
        self.equipped_box.add(self.equipped_label)
        self.equipped_box.set_size_request(self.width, self.label_height)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(self.width, self.height)
        self.fixed.put(self.image, 0, 0)
        self.fixed.put(self.hover_box, 0, self.height - self.label_height)
        self.fixed.put(self.equipped_box, 0, self.height - self.label_height)

        self.button.add(self.fixed)

        # Default, set locked to True and equipped to False.
        self.locked = True
        self.equipped = False

    # Sets whether the picture has a padlock in front or not.
    # locked = True or False
    def set_locked(self, locked):
        self.locked = locked

    def get_locked(self):
        return self.locked

    # Sets whether the picture is equipped
    # equipped = True or False
    def set_equipped(self, equipped):
        self.equipped = equipped

    def get_equipped(self):
        return self.equipped

    # Sets whether the picture is selected, ie whether we should go to the selection screen
    # selected = True or False
    #def set_selected(self, selected):
    #    self.selected = selected

    #def get_selected(self):
    #    return self.selected

    def toggle_equipped(self, arg1=None, arg2=None):
        self.set_equipped(not self.get_equipped())

    # This function contains the styling applied to the picture when the mouse hovers over it.
    def add_hover_style(self, arg1=None, arg2=None):
        self.hover_box.set_visible_window(True)
        self.hover_label.set_visible(True)

    def remove_hover_style(self, arg1=None, arg2=None):
        self.hover_box.set_visible_window(False)
        self.hover_label.set_visible(False)

    # This function contains the styling applied to the picture when it is equipped.
    def add_equipped_style(self, arg1=None, arg2=None):
        self.equipped_box.set_visible_window(True)
        self.equipped_label.set_visible(True)

    def remove_equipped_style(self, arg1=None, arg2=None):
        self.equipped_box.set_visible_window(False)
        self.equipped_label.set_visible(False)
        self.hover_box.set_visible_window(False)
        self.hover_label.set_visible(False)
