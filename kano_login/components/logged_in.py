#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for login screen

from kano.world.functions import remove_token
from kano_login.components import heading
from gi.repository import Gtk


class LoggedIn(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='Kano-Profile')
        self.set_size_request(200, 150)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.ok_button = Gtk.Button("OK")
        self.ok_button.get_style_context().add_class("green_button")
        self.ok_button.connect("clicked", Gtk.main_quit)
        self.button_box = Gtk.Box()
        self.button_box.add(self.ok_button)
        self.alignment = Gtk.Alignment(xscale=1, yscale=1, xalign=0.5, yalign=0.5)
        self.alignment.add(self.button_box)
        self.alignment.set_padding(0, 0, 65, 0)
        self.title = heading.Heading("Logged in!", "You're already logged in")
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_container)
        self.main_container.pack_start(self.title.container, False, False, 0)
        self.main_container.pack_start(self.alignment, False, False, 0)

        # To get a logout button, uncomment out the lines below
        #self.logout_button = Gtk.Button("Log out?")
        #self.logout_button.get_style_context().add_class("logout")
        #self.logout_button.connect("clicked", self.logout)
        #self.main_container.pack_start(self.logout_button, False, False, 0)

        self.connect('delete-event', Gtk.main_quit)
        self.show_all()

    def logged_out_screen(self):
        for child in self.main_container:
            self.main_container.remove(child)
        self.title.set_text("Logged out!", "")
        self.main_container.pack_start(self.title.container, False, False, 0)
        self.main_container.pack_start(self.alignment, False, False, 0)

    def logout(self, event):
        remove_token()
        self.logged_out_screen()

