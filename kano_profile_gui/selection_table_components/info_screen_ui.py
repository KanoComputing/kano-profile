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
import kano_profile_gui.components.cursor as cursor
from kano.profile.profile import set_avatar, set_environment


class InfoScreenUi():
    # Pass array of pictures into class then it can control it's own buttons
    # The current item is the screen we're currenty on
    def __init__(self, item, group, home_button):

        # image width and height
        self.width = 460
        self.height = 448

        # Main container of info screen
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # This means we can control the next and prev controls within the info screen
        self.item_group = group
        self.item_group.set_visible_item(item)

        self.background = Gtk.EventBox()
        self.background.override_background_color(Gtk.StateFlags.NORMAL, self.get_visible_item().get_color())
        self.background.set_size_request(self.width, self.height)

        # For now, just show either the locked image or the unlocked image
        self.image = Gtk.Image()
        self.get_image_at_size()

        # Padlock icon on top locked screen
        self.padlock = icons.set_from_name("padlock")

        fixed = Gtk.Fixed()
        fixed.put(self.image, 0, 0)

        self.fixed = self.create_fixed(fixed)
        self.fixed_container = Gtk.Box()
        self.fixed_container.pack_start(self.fixed, False, False, 0)

        self.background.add(self.fixed_container)

        # Header - contains heading of the badge/swag
        self.header_box = Gtk.EventBox()
        self.header_label = Gtk.Label(self.get_visible_item().title.upper())
        self.header_label.get_style_context().add_class("heading")
        self.header_box.add(self.header_label)
        self.header_box.set_size_request(690 + 44, 44)

        self.info_text = info_text.InfoTextUi(self.get_visible_item())
        self.info_text.set_equip_sensitive(self.get_locked() or self.get_equipped())

        if self.get_visible_item().equipable:
            # This doesn't work because we're not changing the selected_item
            # We need to set a flag or self.selected = True
            # selected_item_screen.info.equip_button.connect("button_press_event", self.equip, cat, selected_item)
            self.info_text.equip_button.connect("button_press_event", self.set_equipped)

        self.box = Gtk.Box()
        self.box.pack_start(self.background, False, False, 0)
        self.box.pack_start(self.info_text.background, False, False, 0)

        self.container.pack_start(self.header_box, False, False, 0)
        self.container.pack_start(self.box, False, False, 0)

        self.change_equipped_style()
        self.change_locked_style()

        # Need to update home button on equipping from this screen
        self.home_button = home_button

    def create_fixed(self, image):
        fixed = Gtk.Fixed()
        prev_arrow = icons.set_from_name("prev_arrow")
        next_arrow = icons.set_from_name("next_arrow")
        prevb = Gtk.Button()
        prevb.set_image(prev_arrow)
        prevb.get_style_context().add_class("transparent")
        prevb.set_size_request(50, 50)
        prevb.connect("button_press_event", self.go_to, -1)
        nextb = Gtk.Button()
        nextb.set_image(next_arrow)
        nextb.get_style_context().add_class("transparent")
        nextb.set_size_request(50, 50)
        nextb.connect("button_press_event", self.go_to, 1)

        cursor.attach_cursor_events(prevb)
        cursor.attach_cursor_events(nextb)

        fixed.put(image, 0, 0)
        fixed.put(prevb, 0, (self.height / 2) - 25)
        fixed.put(nextb, self.width - 50, (self.height / 2) - 25)

        if self.get_visible_item().equipable:
            # Event box containing the EQUIPPED label
            self.equipped_label = Gtk.Label("EQUIPPED")
            self.equipped_box = Gtk.EventBox()
            self.equipped_box.get_style_context().add_class("big_equipped_box")
            self.equipped_box.add(self.equipped_label)
            self.equipped_box.set_size_request(104, 34)

            # Border box of equipped style
            self.equipped_border = Gtk.EventBox()
            self.equipped_border.get_style_context().add_class("big_equipped_border")
            self.equipped_border.set_size_request(120, 50)
            fixed.put(self.equipped_border, 10, 10)
            fixed.put(self.equipped_box, 18, 18)

        return fixed

    def get_color(self):
        return self.get_visible_item().get_color()

    # Update UI of current visible item
    def refresh(self):
        current = self.get_visible_item()
        self.image.set_from_file(self.get_filename_at_size())
        self.header_label.set_text(current.title)
        self.info_text.refresh(current.title, current.get_description(), current.get_color())
        self.background.override_background_color(Gtk.StateFlags.NORMAL, self.get_color())
        self.info_text.set_equip_sensitive((self.get_locked() or self.get_equipped()))
        self.change_equipped_style()
        self.change_locked_style()

    def get_locked(self):
        return self.get_visible_item().get_locked()

    def change_locked_style(self):
        if self.get_locked() and self.padlock.get_parent() is None:
            self.fixed.put(self.padlock, 211, 205)
            self.fixed.show_all()
        elif not self.get_locked() and self.padlock.get_parent() is not None:
            self.fixed.remove(self.padlock)

    def get_equipped_item(self):
        return self.item_group.get_equipped_item()

    def get_equipped(self):
        return self.get_visible_item().get_equipped()

    def set_equipped(self, arg1=None, arg2=None):
        self.item_group.set_equipped_item(self.get_visible_item())
        category = self.get_visible_item().category
        name = self.get_visible_item().name
        subcat = self.get_visible_item().subcategory
        if category == "environments":
            set_environment(name)
        else:
            set_avatar(subcat, name)
        self.info_text.set_equip_sensitive((self.get_locked() or self.get_equipped()))
        self.change_equipped_style()
        self.home_button.update()

    # This function contains the styling applied to the visible item when it is equipped.
    def change_equipped_style(self):
        if self.get_visible_item().equipable:
            self.equipped_border.set_visible_window(self.get_equipped())
            self.equipped_box.set_visible_window(self.get_equipped())
            self.equipped_label.set_visible(self.get_equipped())

    def set_visible_item(self, item):
        self.item_group.set_visible_item(item)

    def get_visible_item(self):
        return self.item_group.get_visible_item()

    def get_image_at_size(self):
        filename = self.get_filename_at_size()
        self.image.set_from_file(filename)

    def get_filename_at_size(self):
        return self.get_visible_item().get_filename_at_size(self.width, self.height)

    def go_to(self, widget, event, move):
        self.item_group.go_to(move)
        self.refresh()
