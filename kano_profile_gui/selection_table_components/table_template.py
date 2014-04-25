#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# table_template.py
#
# Controls interaction between table and info screen

from gi.repository import Gtk
import kano_profile_gui.selection_table_components.selection_table as tab
import kano_profile_gui.selection_table_components.info_screen as info_screen
import kano_profile_gui.components.header as header


# headers: category names, e.g. ["badges"] or ["environments"]
# info: array of information for each category
# equipable: whether each item in the array is equipable (like avatars or environments)
# width and height of the scrolled window
class Template():
    def __init__(self, headers, equipable, width, height):

        self.equipable = equipable

        self.categories = []
        for x in range(len(headers)):
            self.categories.append(tab.Table(headers[x], self.equipable))

        if len(headers) == 2:
            self.head = header.Header(headers[0], headers[1])
            self.head.radiobutton1.connect("toggled", self.on_button_toggled)
        else:
            self.head = header.Header(headers[0])

        for cat in self.categories:
            for pic in cat.pics:
                pic.button.connect("button_press_event", self.go_to_info_screen, cat, pic)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.add_with_viewport(self.categories[0].table)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_size_request(width, height)

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.container.pack_start(self.head.box, False, False, 0)
        self.container.pack_start(self.scrolledwindow, False, False, 0)

    def on_button_toggled(self, radio):
        in_cat1 = radio.get_active()
        for cat in self.categories:
            container = cat.table.get_parent()
            if container is not None:
                container.remove(cat.table)
        for i in self.scrolledwindow.get_children():
                self.scrolledwindow.remove(i)
        if in_cat1:
            self.scrolledwindow.add(self.categories[0].table)
        else:
            self.scrolledwindow.add(self.categories[1].table)
        self.scrolledwindow.show_all()
        self.hide_labels()

    def go_to_info_screen(self, arg1=None, arg2=None, cat=None, selected_item=None):
        selected_item_screen = info_screen.Item(cat, selected_item, self.equipable)
        for i in self.container.get_children():
            self.container.remove(i)
        self.container.add(selected_item_screen.container)
        selected_item_screen.info_text.back_button.connect("button_press_event", self.leave_info_screen)
        if self.equipable:
            # This doesn't work because we're not changing the selected_item
            # We need to set a flag or self.selected = True
            # selected_item_screen.info.equip_button.connect("button_press_event", self.equip, cat, selected_item)
            selected_item_screen.info_text.equip_button.connect("button_press_event", self.equip, cat)
        self.container.show_all()

        # Remove locked images from selected item screen
        selected_item_screen.set_locked()

    def equip(self, arg1=None, arg2=None, cat=None):
        selected_item = cat.get_selected()
        cat.set_equipped(selected_item)
        self.leave_info_screen()

    def leave_info_screen(self, arg1=None, arg2=None):
        for i in self.container.get_children():
            self.container.remove(i)
        self.container.pack_start(self.head.box, False, False, 0)
        self.container.pack_start(self.scrolledwindow, False, False, 0)
        self.container.show_all()
        # Hide all labels on images
        self.hide_labels()

    def hide_labels(self):
        for cat in self.categories:
            cat.hide_labels()
