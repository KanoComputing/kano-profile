#!/usr/bin/env python

# menu_bar.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

from gi.repository import Gtk
import kano_profile_gui.components.icons as icons
import kano_profile_gui.components.cursor as cursor
import kano_profile_gui.menu_bar_components.home_button as home_button


class MenuBar():
    def __init__(self, WINDOW_WIDTH):

        # Makes it easier to centre other widgets even if we change this
        self.height = 96

        # This is here due to a Gtk bug specific to 3.10. Widgets packed in Fixed containers have their z-order
        # depending on their widget type, not the order they were packed.
        # Hacky fix - for all parent containers to be Gtk.Box()s
        self.box = Gtk.Box()

        # This is to give the correct colour of the top bar as Event Boxes are the only containers that we can colour
        # This contains everything, but can't pack directly into as is only a simple container
        self.background = Gtk.EventBox()
        self.background.set_size_request(WINDOW_WIDTH, self.height)
        self.background.style = self.background.get_style_context()
        self.background.style.add_class('menu_bar_container')

        self.container = Gtk.Box()

        # Home button
        self.home_button = home_button.HomeButton()
        self.home_button.button.connect('button_press_event', self.activate_label)

        name_array = ['Badges', 'Swag', 'Challenges']
        self.badges_button = Gtk.Button()
        self.swag_button = Gtk.Button()
        self.challenges_button = Gtk.Button()
        self.button_array = [self.badges_button, self.swag_button, self.challenges_button]
        self.badges_label = Gtk.Label()
        self.swag_label = Gtk.Label()
        self.challenges_label = Gtk.Label()
        self.label_array = [self.badges_label, self.swag_label, self.challenges_label]

        for x in range(3):
            label = self.label_array[x]
            label.set_text(name_array[x].upper())

            # This sets the font size, weight and initial colour.  This is only because Gtk 3.4 has a bug in it.
            label.get_style_context().add_class("menu_bar_label")
            icon = icons.set_from_name(name_array[x].lower())

            container = Gtk.Box()
            container.pack_start(icon, False, False, 0)
            container.pack_start(label, False, False, 10)

            button = self.button_array[x]
            button.set_can_focus(False)
            button.get_style_context().add_class("menu_bar_button")
            button.add(container)
            button.connect('button_press_event', self.activate_label)

        # Close button
        cross = icons.set_from_name("cross")
        cross.set_padding(5, 5)
        self.close_button = Gtk.Button()
        self.close_button.set_image(cross)
        self.close_button.set_can_focus(False)
        self.close_button.get_style_context().add_class("menu_bar_button")
        self.close_button.get_style_context().add_class("close_button")
        self.close_button.connect("button_press_event", self.close_window)
        self.close_button.set_alignment(xalign=1, yalign=0)

        self.container.pack_start(self.home_button.button, False, False, 0)
        self.container.pack_end(self.close_button, False, False, 0)
        self.container.pack_end(self.challenges_button, False, False, 0)
        self.container.pack_end(self.swag_button, False, False, 0)
        self.container.pack_end(self.badges_button, False, False, 0)
        self.container.set_size_request(WINDOW_WIDTH, self.height)
        self.background.add(self.container)

        cursor.attach_cursor_events(self.close_button)
        cursor.attach_cursor_events(self.badges_button)
        cursor.attach_cursor_events(self.swag_button)
        cursor.attach_cursor_events(self.challenges_button)
        cursor.attach_cursor_events(self.home_button.button)

        self.box.add(self.background)

    def activate_label(self, widget, event):

        for label in self.label_array:
            label.get_style_context().remove_class("active_label")
            label.get_style_context().add_class("inactive_label")

        if widget in self.button_array:
            index = self.button_array.index(widget)
            label_style = self.label_array[index].get_style_context()
            label_style.remove_class("inactive_label")
            label_style.add_class("active_label")
            self.home_button.set_activate(False)
        else:
            self.home_button.set_activate(True)

    def close_window(self, event, button):
        Gtk.main_quit()


