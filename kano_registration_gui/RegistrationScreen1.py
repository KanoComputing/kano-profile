#!/usr/bin/env python

# RegistrationScreen1.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk
from kano.gtk3.heading import Heading
from kano_registration_gui.RegistrationScreen2 import RegistrationScreen2


# Page 1 is the character personalisation
class RegistrationScreen1(Gtk.Box):

    def __init__(self, win):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.win = win
        self.win.set_decorated(True)
        self.win.set_main_widget(self)

        title = Heading('Make your Character',
                        'Change how the character looks')

        self.pack_start(title.container, False, False, 0)
        self.pack_start(self.win.char_creator, False, False, 0)

        # No back button on first page
        self.page_control = self.win.create_page_control(1, "", "NEXT")
        self.pack_end(self.page_control, False, False, 0)
        self.page_control.connect("next-button-clicked", self.next_page)

        self.win.show_all()

        # This hides the pop up category when using the back button
        self.win.char_creator._hide_pop_ups()

        # Show the Faces category
        self.win.char_creator.show_pop_up_menu_for_category("Faces")
        self.win.char_creator.select_category_button("Faces")

    def next_page(self, widget):
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.win.get_window().set_cursor(watch_cursor)
        self.page_control.disable_buttons()

        # Force the button UI to update
        while Gtk.events_pending():
            Gtk.main_iteration()

        # This used to be in a separate thread.
        self.save_character_and_go_next()

    def save_character_and_go_next(self):
        self.win.char_creator.save()

        self.win.remove_main_widget()

        # This is here so when we repack in the above screen,
        # we don't get an error.
        self.remove(self.win.char_creator)
        self.win.get_window().set_cursor(None)

        RegistrationScreen2(self.win)
