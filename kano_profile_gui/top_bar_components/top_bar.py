#!/usr/bin/env python

# top_bar.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

from gi.repository import Gtk, Gdk
import kano_profile_gui.components.icons as icons
import kano_profile_gui.top_bar_components.home_button as home_button


class TopBar():
    def __init__(self, WINDOW_WIDTH):

        # Makes it easier to centre other widgets even if we change this
        self.height = 96

        # This is to give the correct colour of the top bar as Event Boxes are the only containers that we can colour
        # This contains everything, but can't pack directly into as is only a simple container
        self.background = Gtk.EventBox()
        self.background.set_size_request(WINDOW_WIDTH, self.height)
        self.background.style = self.background.get_style_context()
        self.background.style.add_class('top_bar_container')

        self.container = Gtk.Grid()

        # Home button
        self.home_button = home_button.HomeButton(1)
        self.home_button.button.connect('button_press_event', self.activate_label)

        name_array = ['Badges', 'Swag', 'Challenges']
        self.badges_button = Gtk.Button()
        self.swag_button = Gtk.Button()
        self.challenges_button = Gtk.Button()
        self.button_array = [self.badges_button, self.swag_button, self.challenges_button]
        badges_label = Gtk.Label()
        swag_label = Gtk.Label()
        challenges_label = Gtk.Label()
        self.label_array = [badges_label, swag_label, challenges_label]

        for x in range(3):
            label = self.label_array[x]
            label.set_text(name_array[x].upper())
            label.get_style_context().add_class("top_bar_label")

            icon = icons.set_from_name(name_array[x].lower())

            container = Gtk.Box()
            container.pack_start(icon, False, False, 0)
            container.pack_start(label, False, False, 10)

            button = self.button_array[x]
            button.set_size_request(WINDOW_WIDTH / 5, self.height)
            button.set_can_focus(False)
            button.get_style_context().add_class("top_bar_button")
            button.add(container)
            button.connect('button_press_event', self.activate_label)

        # Close button
        cross = icons.set_from_name("cross")
        close_button = Gtk.Button()
        close_button.set_image(cross)
        close_button.set_size_request(10, 10)
        close_button.set_can_focus(False)
        close_button.get_style_context().add_class("top_bar_button")
        close_button.get_style_context().add_class("close_button")
        close_button.connect("button_press_event", close_window)
        close_button.set_alignment(xalign=1, yalign=0)

        self.container.attach(self.home_button.button, 0, 0, 1, 3)
        self.container.attach(self.badges_button, 1, 0, 1, 3)
        self.container.attach(self.swag_button, 2, 0, 1, 3)
        self.container.attach(self.challenges_button, 3, 0, 1, 3)
        self.container.attach(close_button, 4, 0, 1, 1)
        self.container.set_size_request(WINDOW_WIDTH, self.height)

        self.background.add(self.container)

    # TODO: Home button uses this function, change this
    def activate_label(self, widget, event):

        for label in self.label_array:
            label.get_style_context().remove_class("top_bar_label_active")
            label.get_style_context().add_class("top_bar_label")
            # Doesn't matter the colour you pass here, just needs to force Gtk to re-style the label and notice the change of class
            label.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("green"))

        index = self.button_array.index(widget)

        label_style = self.label_array[index].get_style_context()

        label_style.remove_class("top_bar_label")
        label_style.add_class("top_bar_label_active")


def close_window(event, button):
        Gtk.main_quit()


