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
from kano_profile_gui.images import get_image


class Item():
    # Pass array of pictures into class then it can control it's own buttons
    # The current item is the screen we're currenty on
    def __init__(self, category, current_item, equip):

        # image width and height
        self.width = 400
        self.height = 400

        # Boolean we pass to the text box to decide whether we put an equip button
        self.equip = equip

        # Main container of info screen
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.category = category
        self.array = category.pics
        self.current = current_item

        self.image = Gtk.Image()
        self.set_image()

        # Make the item who's info screen it is the selected item
        self.category.set_selected(self.current)

        # Header - contains heading of the badge/swag
        self.header_box = Gtk.EventBox()
        self.header_label = Gtk.Label(self.current.heading)
        self.header_label.get_style_context().add_class("heading")
        self.header_box.add(self.header_label)
        self.header_box.set_size_request(690 + 44, 44)

        prev_arrow = icons.set_from_name("prev_arrow")
        next_arrow = icons.set_from_name("next_arrow")

        self.prev = Gtk.Button()
        self.prev.set_image(prev_arrow)
        self.prev.connect("button_press_event", self.go_to_prev)
        self.next = Gtk.Button()
        self.next.set_image(next_arrow)
        self.next.connect("button_press_event", self.go_to_next)

        # To get the buttons overlaying the main picture
        self.fixed = Gtk.Fixed()
        self.fixed.put(self.image, 0, 0)
        self.fixed.put(self.prev, 0, self.height / 2)
        self.fixed.put(self.next, self.width - 35, self.height / 2)

        self.info = info_text.Info(700 - self.width, self.height, self.current.heading, self.current.description, self.equip)

        self.box = Gtk.Box()
        self.box.pack_start(self.fixed, False, False, 0)
        self.box.pack_start(self.info.background, False, False, 0)

        self.container.pack_start(self.header_box, False, False, 0)
        self.container.pack_start(self.box, False, False, 0)

        #self.box.pack_start(self.fixed, False, False, 0)
        #self.box.pack_start(self.info.background, False, False, 0)

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
        self.set_image()

    def set_image(self):
         # filename of picture
        filename = get_image(self.current.item, self.current.group, self.width)
        self.image.set_from_file(filename)
