#!/usr/bin/env python

# info_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# If an environment/avatar/badge is selected, we go to this screen to show more info

from gi.repository import Gtk, GdkPixbuf
import kano_profile_gui.selection_table_components.info_text as info_text
import kano_profile_gui.components.icons as icons
import kano_profile_gui.components.constants as constants


class InfoScreen():
    # Pass array of pictures into class then it can control it's own buttons
    # The current item is the screen we're currenty on
    def __init__(self, category, current_item, equip):

        # image width and height
        self.width = 460
        self.height = 448

        # Boolean we pass to the text box to decide whether we put an equip button
        self.equip = equip

        # Main container of info screen
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.category = category
        self.array = category.pics
        self.current = current_item

        self.background = Gtk.EventBox()
        self.background.override_background_color(Gtk.StateFlags.NORMAL, self.current.bg_color)
        self.background.set_size_request(self.width, self.height)

        self.image = self.get_image_at_size()
        self.locked_image = self.get_image_at_size()
        self.greybox = Gtk.EventBox()
        self.greybox.get_style_context().add_class("locked_box")
        self.greybox.set_size_request(self.width, self.height)
        self.padlock = Gtk.Image()
        self.padlock.set_from_file(constants.media + "/images/icons/Level-4.png")

        fixed = Gtk.Fixed()
        fixed.put(self.image, 0, 0)

        locked_fixed = Gtk.Fixed()
        locked_fixed.put(self.locked_image, 0, 0)
        locked_fixed.put(self.greybox, 0, 0)
        locked_fixed.put(self.padlock, 180, 180)
        locked_fixed.set_size_request(self.width, self.height)

        self.fixed = self.create_fixed(fixed)
        self.locked_fixed = self.create_fixed(locked_fixed)
        self.fixed_container = Gtk.Box()

        # Make the item who's info screen it is the selected item
        self.category.set_selected(self.current)

        # Header - contains heading of the badge/swag
        self.header_box = Gtk.EventBox()
        self.header_label = Gtk.Label(self.current.title)
        self.header_label.get_style_context().add_class("heading")
        self.header_box.add(self.header_label)
        self.header_box.set_size_request(690 + 44, 44)

        self.info_text = info_text.InfoText(self.current.title, self.current.get_description(), self.equip)

        self.box = Gtk.Box()
        self.box.pack_start(self.fixed_container, False, False, 0)
        self.box.pack_start(self.info_text.background, False, False, 0)

        self.background.add(self.box)

        self.container.pack_start(self.header_box, False, False, 0)
        self.container.pack_start(self.background, False, False, 0)

        self.set_locked()

    def create_fixed(self, image):
        prev_arrow = icons.set_from_name("prev_arrow")
        next_arrow = icons.set_from_name("next_arrow")

        prevb = Gtk.Button()
        prevb.set_image(prev_arrow)
        prevb.connect("button_press_event", self.go_to_prev)
        nextb = Gtk.Button()
        nextb.set_image(next_arrow)
        nextb.connect("button_press_event", self.go_to_next)

        fixed = Gtk.Fixed()
        if self.current.category == "environments":
            fixed.put(image, 0, 0)
        else:
            fixed.put(image, 6, 0)
        fixed.put(prevb, 0, self.height / 2)
        fixed.put(nextb, self.width - 35, self.height / 2)

        return fixed

    def go_to_next(self, arg1=None, arg2=None):
        index = self.array.index(self.current)
        self.current = self.array[(index + 1) % len(self.array)]
        self.refresh()

    def go_to_prev(self, arg1=None, arg2=None):
        index = self.array.index(self.current)
        self.current = self.array[(index - 1) % len(self.array)]
        self.refresh()

    def refresh(self):
        self.category.set_selected(self.current)
        self.image.set_from_pixbuf(self.get_pixbuf_at_size())
        self.locked_image.set_from_pixbuf(self.get_pixbuf_at_size())
        self.header_label.set_text(self.current.title)
        self.info_text.refresh(self.current.title, self.current.get_description())
        self.set_locked()
        self.background.override_background_color(Gtk.StateFlags.NORMAL, self.current.bg_color)
        self.container.show_all()

    def get_filename_at_size(self):
        return self.current.get_filename_at_size(self.width, self.height)

    def set_locked(self, locked=None):
        if locked is None:
            locked = self.current.locked
        else:
            self.current.locked = locked
        for child in self.fixed_container.get_children():
            self.fixed_container.remove(child)

        if locked:
            self.fixed_container.add(self.locked_fixed)
        else:
            self.fixed_container.add(self.fixed)

    def get_image_at_size(self):
        image = Gtk.Image()
        filename = self.get_filename_at_size()
        image.set_from_file(filename)
        return image

    def get_pixbuf_at_size(self):
        filename = self.get_filename_at_size()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        return pixbuf
