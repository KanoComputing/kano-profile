#!/usr/bin/env python

# logged_in.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for login screen

from kano_world.functions import remove_token
from kano.gtk3.buttons import KanoButton
from kano.gtk3.heading import Heading
from gi.repository import Gtk
import kano.gtk3.cursor as cursor


class LoggedIn(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='Profile')
        self.set_size_request(200, 150)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.ok_button = KanoButton("OK")
        self.ok_button.pack_and_align()
        self.ok_button.set_padding(20, 20, 0, 0)
        self.ok_button.connect("clicked", Gtk.main_quit)
        self.title = Heading("Logged in!", "You're already logged in")
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_container)
        self.main_container.pack_start(self.title.container, False, False, 0)
        self.main_container.pack_start(self.ok_button.align, False, False, 0)

        # To get a logout button, uncomment out the lines below
        #self.logout_button = OrangeButton("Log out?")
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

    def close_window(self, event, button, win):
        self.ok_button.disconnect_handlers()
        cursor.arrow_cursor(None, None, win)
        Gtk.main_quit()

