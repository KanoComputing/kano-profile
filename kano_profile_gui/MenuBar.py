#!/usr/bin/env python

# MenuBar.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

from gi.repository import Gtk, GObject
from kano.gtk3.cursor import attach_cursor_events
from kano_world.functions import get_mixed_username
from kano_profile.badges import calculate_kano_level
from kano_profile_gui.components.icons import get_ui_icon


# In case we change the colour of the menu bar, we have a background
# across all of them.
class MenuBar(Gtk.EventBox):
    __gsignals__ = {
        'home-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'menu-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, win_width):

        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class('menu_bar_container')

        self.height = 110
        self.width = win_width
        self.set_size_request(self.width, self.height)

        hbox = Gtk.Box()
        self.add(hbox)

        self.buttons = {}
        self.selected = None

        # Home button
        self.home_button = HomeButton()
        self.home_button.connect("clicked", self.emit_home_signal)
        self.home_button.connect("clicked", self.set_selected_wrapper, "CHARACTER")
        hbox.pack_start(self.home_button, False, False, 0)

        close_button = self._create_cross_button()
        hbox.pack_end(close_button, False, False, 0)
        close_button.connect("clicked", self.close_window)

        name_array = ['SAVES', 'BADGES', 'CHARACTER']
        for name in name_array:
            button = MenuButton(name)
            button.connect("clicked", self.emit_menu_signal, name)
            button.connect("clicked", self.set_selected_wrapper, name)
            hbox.pack_end(button, False, False, 0)

            # add to the self.buttons dictionary
            self.buttons[name] = {}
            self.buttons[name]["button"] = button

            # HACKY: avoiding packing the label divider after the last element
            if name != "CHARACTER":
                label = self._create_divider_label()
                hbox.pack_end(label, False, False, 0)

            attach_cursor_events(button)

        # initialise with the CHARACTER button selected
        self.set_selected("CHARACTER")

    def _create_divider_label(self):
        label = Gtk.Label("|")
        label.get_style_context().add_class("button_divider")
        return label

    def _create_cross_button(self):
        # Close button
        cross_icon = get_ui_icon("cross")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        close_button = Gtk.Button()
        close_button.add(box)
        box.add(cross_icon)
        close_button.get_style_context().add_class("close_button")
        close_button.connect("clicked", self.close_window)
        attach_cursor_events(close_button)

        return close_button

    def emit_menu_signal(self, widget, name):
        self.emit("menu-button-clicked", name)

    def emit_home_signal(self, widget):
        self.emit('home-button-clicked', 'CHARACTER')

    def get_selected_button(self):
        return self.selected

    def set_selected_wrapper(self, widget, name):
        self.set_selected(name)

    def set_selected(self, name):
        self.selected = name

        for button_id, id_dict in self.buttons.iteritems():
            button = self.buttons[button_id]['button']
            button.selected = False
            button.remove_selected_style()

        button = self.buttons[name]['button']
        button.selected = True
        button.set_selected_style()

    def close_window(self, button):
        Gtk.main_quit()


class HomeButton(Gtk.Button):

    def __init__(self):
        Gtk.Button.__init__(self)
        attach_cursor_events(self)
        self.get_style_context().add_class('home_button')

        # Get the username or kano world name
        # Get username here
        username = get_mixed_username()
        if len(username) > 12:
            username = username[:12] + '...'

        # Info about the different settings
        title_label = Gtk.Label(username, xalign=0)
        title_label.get_style_context().add_class("home_button_name")

        level, progress, _ = calculate_kano_level()
        level_label = Gtk.Label("Level {}".format(level), xalign=0)
        level_label.get_style_context().add_class("home_button_level")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(title_label, False, False, 0)
        vbox.pack_start(level_label, False, False, 0)

        self.add(vbox)


class MenuButton(Gtk.Button):

    def __init__(self, name):
        self.name = name

        Gtk.Button.__init__(self)
        self.selected = False

        # an icon may be added later
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        label = Gtk.Label(name)
        vbox.add(label)

        # Makes it easy to access exactly where the icon is
        self.icon_align = Gtk.Alignment(xscale=0, xalign=0.5)
        vbox.pack_start(self.icon_align, False, False, 0)

        self.get_style_context().add_class("menu_bar_button")
        self.set_property("always-show-image", True)

        # select on hover over
        self.connect("enter-notify-event", self.set_selected_wrapper)
        self.connect("leave-notify-event", self.remove_selected_wrapper)

    def set_selected_style(self):
        '''We shouldn't have to worry about applying this when it
        already has been applied.
        '''

        if not self.icon_align.get_children():
            self.get_style_context().add_class("selected")
            icon = get_ui_icon("dropdown_arrow")
            self.icon_align.add(icon)
            self.show_all()

        self.icon_align.show()

    def remove_selected_style(self):
        self.get_style_context().remove_class("selected")
        for child in self.icon_align.get_children():
            self.icon_align.remove(child)

    def set_selected_wrapper(self, widget, args):
        self.set_selected_style()

    def remove_selected_wrapper(self, widget, args):
        if not self.selected:
            self.remove_selected_style()
