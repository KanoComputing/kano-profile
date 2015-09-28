#!/usr/bin/env python

# MenuBar.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This controls the styling of the (pretend) top window bar.

import os
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

    def __init__(self, win_width, quests):

        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class('menu_bar_container')

        self.height = 110
        self.width = win_width
        self.set_size_request(self.width, self.height)

        self._quests = quests

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

        name_array = ['BADGES', 'CHARACTER'] # TODO: add 'QUESTS' to enable
        for name in name_array:
            button = MenuButton(name, self._quests)
            button.connect("clicked", self.emit_menu_signal, name)
            button.connect("clicked", self.set_selected_wrapper, name)
            hbox.pack_end(button, False, False, 0)

            # add to the self.buttons dictionary
            self.buttons[name] = {}
            self.buttons[name]["button"] = button

            if name == "QUESTS":
                # check the notification image
                button.check_for_notification()

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

    def get_button(self, name):
        return self.buttons[name]["button"]

    def close_window(self, button):
        Gtk.main_quit()

    def disable_buttons(self):
        """ Disable all the buttons except for the exit button.
        The latter's sensitivity is not altered
        """
        self._set_button_sensitivity(False)

    def enable_buttons(self):
        """ Enable all the menu buttons. The exit button's sensitivity is
        not altered
        """
        self._set_button_sensitivity(True)

    def _set_button_sensitivity(self, sensitivity_value):
        """ Keep all the buttons whose sensitivity we want to control here
        """
        self.home_button.set_sensitive(sensitivity_value)
        for button in self.buttons.itervalues():
            button["button"].set_sensitive(sensitivity_value)


class HomeButton(Gtk.Button):

    def __init__(self):
        Gtk.Button.__init__(self)
        attach_cursor_events(self)
        self.get_style_context().add_class('home_button')

        # Get the username or kano world name
        # Get username here
        username = get_mixed_username()
        if len(username) > 12:
            username = username[:12] + u'\N{HORIZONTAL ELLIPSIS}'

        # Info about the different settings
        title_label = Gtk.Label(username, xalign=0)
        title_label.get_style_context().add_class("home_button_name")

        level, dummy, dummy = calculate_kano_level()
        level_label = Gtk.Label(_("Level {}").format(level), xalign=0)
        level_label.get_style_context().add_class("home_button_level")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(title_label, False, False, 0)
        vbox.pack_start(level_label, False, False, 0)

        self.add(vbox)


class MenuButton(Gtk.Button):

    kdesk_num_path = "/usr/share/kano-desktop/images/world-numbers"

    def __init__(self, name, quests):
        self.name = name
        self._quests = quests

        Gtk.Button.__init__(self)
        self.selected = False

        # an icon may be added later
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        self.notification_img = Gtk.Image()
        self.notification_img.set_size_request(29, 29)
        vbox.pack_start(self.notification_img, False, False, 0)

        label = Gtk.Label(name)
        vbox.pack_start(label, False, False, 0)

        # Makes it easy to access exactly where the icon is
        self.icon_align = Gtk.Alignment(xscale=0, xalign=0.5)
        vbox.pack_start(self.icon_align, False, False, 0)

        self.get_style_context().add_class("menu_bar_button")
        self.set_property("always-show-image", True)

        # select on hover over
        self.connect("enter-notify-event", self.set_selected_wrapper)
        self.connect("leave-notify-event", self.remove_selected_wrapper)

    def _get_show_mission_notification(self):
        # This could read from kano-profile based on the name
        # Returns an int between 0-10 inclusive.

        active_quests = self._quests.list_active_quests()
        fulfilled = 0

        for quest in active_quests:
            if quest.is_fulfilled():
                fulfilled += 1

        return fulfilled

    def _set_show_mission_notification(self, show_notification):
        self.show_notification = show_notification

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

    def check_for_notification(self):
        # Decide whether to show the notifications for the button
        num = self._get_show_mission_notification()
        if num > 0:
            num = str(num)

            # pack number icon next to it
            num_path = os.path.join(
                self.kdesk_num_path,
                "{}.png".format(num)
            )
            self.notification_img.set_from_file(num_path)
            return True
        else:
            self.notification_img.clear()
            return False
