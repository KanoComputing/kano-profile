#!/usr/bin/env python

# menu_bar.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

from gi.repository import Gtk, GObject
import kano_profile_gui.components.icons as icons
from kano_profile_gui.components.cursor import attach_cursor_events
from kano_world.functions import get_mixed_username
from kano_profile.badges import calculate_kano_level


# In case we change the colour of the menu bar, we have a background
# across all of them.
class MenuBar(Gtk.EventBox):

    def __init__(self, win_width):

        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class('menu_bar_container')

        self.height = 96
        self.width = win_width

        self.set_size_request(win_width, self.height)
        self.hbox = Gtk.Box()
        self.add(self.hbox)

        self.buttons = {}
        self.selected = None

        # Home button
        self.home_button = HomeButton()

        name_array = ['CHARACTER', 'BADGES', 'SAVES']
        for name in name_array:
            button = MenuButton(name)
            self.hbox.pack_start(button, False, False, 0)
            self._buttons[name] = {}
            self._buttons[name]['button'] = button
            attach_cursor_events(button)

        # Close button
        cross = icons.set_from_name("cross")
        cross.set_padding(5, 5)
        self.close_button = Gtk.Button()
        self.close_button.set_image(cross)
        self.close_button.get_style_context().add_class("menu_bar_button")
        self.close_button.get_style_context().add_class("close_button")
        self.close_button.connect("clicked", self.close_window)

        # TODO: pack the close button in the container

    def get_selected_button(self):
        return self.selected

    def set_selected(self, name):
        self.selected = name

    def close_window(self, button):
        Gtk.main_quit()


class HomeButton(Gtk.Button):
    __gsignals__ = {
        'home-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, (None,))
    }

    def __init__(self):
        Gtk.Button.__init__(self)
        self.connect("clicked", self.emit_signal)

        # Get the username or kano world name
        # Get username here
        username = get_mixed_username()
        if len(self.username) > 12:
            self.username = self.username[:12] + '...'

        level, progress = calculate_kano_level()

        # Info about the different settings
        title_label = Gtk.Label(username)
        title_label.get_style_context().add_class("home_button_name")

        level_label = Gtk.Label("Level {}".format(level))
        title_label.get_style_context().add_class("home_button_level")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(title_label, False, False, 0)
        vbox.pack_start(level_label, False, False, 0)

        self.add(vbox)

    def emit_signal(self, widget):
        self.emit('home-button-clicked')


class MenuButton(Gtk.Button):
    __gsignals__ = {
        'menu-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, name):
        self.name = name

        Gtk.Button.__init__(self)

        # an icon may be added later
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        label = Gtk.Label(name)
        vbox.add(label)

        self.get_style_context().add_class("menu_button")
        self.connect("clicked", self.emit_signal)

    def emit_signal(self, widget):
        self.emit("menu-button-clicked", self.name)
