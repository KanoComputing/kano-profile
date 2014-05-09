#!/usr/bin/env python

# info_screen2.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI over item_group

#!/usr/bin/env python

# info_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# If an environment/avatar/badge is selected, we go to this screen to show more info

from gi.repository import Gtk
import kano_profile_gui.selection_table_components.info_text_ui as info_text
import kano_profile_gui.components.icons as icons


class InfoScreenUi():
    # Pass array of pictures into class then it can control it's own buttons
    # The current item is the screen we're currenty on
    def __init__(self, item_group):

        # image width and height
        self.width = 460
        self.height = 448

        # Main container of info screen
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.items = item_group

        self.background = Gtk.EventBox()
        self.background.override_background_color(Gtk.StateFlags.NORMAL, self.items.get_color())
        self.background.set_size_request(self.width, self.height)

        # For now, just show either the locked image or the unlocked image
        self.image = Gtk.Image()
        self.get_image_at_size()

        fixed = Gtk.Fixed()
        fixed.put(self.image, 0, 0)

        self.fixed = self.create_fixed(fixed)
        self.fixed_container = Gtk.Box()
        self.fixed_container.pack_start(self.fixed, False, False, 0)

        self.background.add(self.fixed_container)

        visible_item = self.get_visible_item()

        # Header - contains heading of the badge/swag
        self.header_box = Gtk.EventBox()
        self.header_label = Gtk.Label(visible_item.title.upper())
        self.header_label.get_style_context().add_class("heading")
        self.header_box.add(self.header_label)
        self.header_box.set_size_request(690 + 44, 44)

        self.info_text = info_text.InfoTextUi(visible_item)
        self.info_text.set_equip_locked(self.get_locked())

        self.box = Gtk.Box()
        self.box.pack_start(self.background, False, False, 0)
        self.box.pack_start(self.info_text.background, False, False, 0)

        self.container.pack_start(self.header_box, False, False, 0)
        self.container.pack_start(self.box, False, False, 0)

    def create_fixed(self, image):
        fixed = Gtk.Fixed()

        if self.items.get_number_of_items() > 1:
            prev_arrow = icons.set_from_name("prev_arrow")
            next_arrow = icons.set_from_name("next_arrow")
            prevb = Gtk.Button()
            prevb.set_image(prev_arrow)
            prevb.get_style_context().add_class("transparent")
            prevb.connect("button_press_event", self.go_to_prev)
            nextb = Gtk.Button()
            nextb.set_image(next_arrow)
            nextb.get_style_context().add_class("transparent")
            nextb.connect("button_press_event", self.go_to_next)
            fixed.put(image, 0, 0)
            fixed.put(prevb, 0, self.height / 2)
            fixed.put(nextb, self.width - 35, self.height / 2)
        else:
            fixed.put(image, 0, 0)

        return fixed

    def set_visible_item(self, item):
        self.items.set_visible_item(item)
        self.get_filename_at_size()

    def get_visible_item(self):
        return self.items.get_visible_item()

    def get_color(self):
        return self.get_visible_item().get_color()

    def go_to_next(self, arg1=None, arg2=None):
        self.items.go_to(1)
        self.refresh()

    def go_to_prev(self, arg1=None, arg2=None):
        self.items.go_to(-1)
        self.refresh()

    def refresh(self):
        current = self.get_visible_item()
        self.items.set_visible_item(current)
        self.image.set_from_file(self.get_filename_at_size())
        self.header_label.set_text(current.title)
        self.info_text.refresh(current.title, current.get_description())
        self.refresh_bg_color()
        self.container.show_all()
        self.info_text.set_equip_locked(self.get_locked())

    def refresh_bg_color(self):
        self.background.override_background_color(Gtk.StateFlags.NORMAL, self.get_visible_item().get_color())

    def get_filename_at_size(self):
        return self.get_visible_item().get_filename_at_size(self.width, self.height)

    def refresh_background(self):
        self.background.override_background_color(Gtk.StateFlags.NORMAL, self.get_visible_item().get_color())

    def get_locked(self):
        return self.get_visible_item().get_locked()

    def get_image_at_size(self):
        filename = self.get_filename_at_size()
        self.image.set_from_file(filename)
