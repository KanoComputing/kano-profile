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


class Item():
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

        self.image = self.set_image_height()
        self.locked_image = self.set_image_height()
        self.greybox = Gtk.EventBox()
        self.greybox.get_style_context().add_class("locked_box")
        #self.greybox.get_style_context().add_class("black")
        self.greybox.set_size_request(self.width, self.height)
        self.padlock = Gtk.Image()
        self.padlock.set_from_file(constants.media + "/images/icons/Level-4.png")
        # fixed is the locked image
        fixed = Gtk.Fixed()
        fixed.put(self.locked_image, 0, 0)
        fixed.put(self.greybox, 0, 0)
        fixed.put(self.padlock, 180, 180)
        fixed.set_size_request(self.width, self.height)

        self.fixed = self.create_fixed(self.image)
        self.locked_fixed = self.create_fixed(fixed)
        self.fixed_container = Gtk.Box()

        # Make the item who's info screen it is the selected item
        self.category.set_selected(self.current)

        # Header - contains heading of the badge/swag
        self.header_box = Gtk.EventBox()
        self.header_label = Gtk.Label(self.current.title)
        self.header_label.get_style_context().add_class("heading")
        self.header_box.add(self.header_label)
        self.header_box.set_size_request(690 + 44, 44)

        #prev_arrow = icons.set_from_name("prev_arrow")
        #next_arrow = icons.set_from_name("next_arrow")

        #self.prev = Gtk.Button()
        #self.prev.set_image(prev_arrow)
        #self.prev.connect("button_press_event", self.go_to_prev)
        #self.next = Gtk.Button()
        #self.next.set_image(next_arrow)
        #self.next.connect("button_press_event", self.go_to_next)

        #self.locked = locked_screen.Screen(self.width, self.height, 50, 50)
        #self.locked.fixed.put(self.prev, 0, self.height / 2)
        #self.locked.fixed.put(self.next, self.width - 35, self.height / 2)

        # To get the buttons overlaying the main picture
        #self.fixed = Gtk.Fixed()
        #self.fixed.put(self.image, 0, 0)
        #self.fixed.put(self.locked.fixed, 0, 0)
        #self.fixed.put(self.prev, 0, self.height / 2)
        #self.fixed.put(self.next, self.width - 35, self.height / 2)

        self.info_text = info_text.Info(self.current.title, self.current.get_description(), self.equip)

        self.box = Gtk.Box()
        self.box.pack_start(self.fixed_container, False, False, 0)
        self.box.pack_start(self.info_text.background, False, False, 0)

        self.container.pack_start(self.header_box, False, False, 0)
        self.container.pack_start(self.box, False, False, 0)
        #self.container.pack_start(self.box, False, False, 0)

        #self.set_image()
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
        #self.image.set_from_file(self.set_filename())
        #self.locked_image.set_from_file(self.set_filename())
        self.image.set_from_pixbuf(self.set_pixbuf_height())
        self.locked_image.set_from_pixbuf(self.set_pixbuf_height())
        self.header_label.set_text(self.current.title)
        self.info_text.refresh(self.current.title, self.current.get_description())
        self.set_locked()
        self.container.show_all()

    def set_image(self):
        image = Gtk.Image()
        image.set_from_file(self.set_filename())
        #self.set_locked()
        return image

    def set_filename(self):
        return self.current.get_filename_at_height(self.height)

    """def set_locked(self, locked=None):
                    if locked is None:
                        locked = self.current.locked
                    else:
                        self.current.locked = locked
                    self.locked.box.set_visible_window(locked)
                    self.locked.padlock.set_visible(locked)
                    self.locked.box.set_above_child(True)"""

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

    def set_image_height(self):
        #filename = self.get_filename_at_height(height_of_image)
        pixbuf = self.set_pixbuf_height()
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)
        return image

    def set_pixbuf_height(self):
        filename = self.current.get_filename_at_height(self.height)
        print "info screen filename = " + str(filename)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        if self.current.category == "environments":
            pixbuf = pixbuf.new_subpixbuf(177, 0, self.height, self.height)  # x = 177
        else:
            pixbuf = pixbuf.new_subpixbuf(0, 0, self.height, self.height)
        return pixbuf
