#!/usr/bin/env python

# main.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for login screen

from gi.repository import Gtk, Gdk
import components.top_bar as top_bar
import home


class MainWindow(Gtk.Window):

    def __init__(self):
        # Create main window
        Gtk.Window.__init__(self, title='Kano-Profile')
        self.WINDOW_HEIGHT = 380
        self.WINDOW_WIDTH = 500

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.set_size_request(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Remove decoration
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Dynamic box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.top_bar = top_bar.Top_bar(self.WINDOW_WIDTH)
        self.top_bar.prev_button.connect("clicked", self.on_prev)
        self.top_bar.next_button.connect("clicked", self.on_next)

        self.grid.attach(self.top_bar.background, 0, 0, 3, 1)
        self.grid.attach(self.box, 1, 1, 1, 1)

        # init home screen
        home.activate(self, self.box)

    # Takes you back to the home screen (on pressing prev button)
    def on_prev(self, arg2=None):
        for i in self.box.get_children():
            self.box.remove(i)

        self.top_bar.disable_prev()
        self.top_bar.enable_next()
        home.activate(self, self.box)
        self.show_all()

    # When clicking next in the home screen - takes you to the last screen you visited
    def on_next(self, widget=None):
        for i in self.box.get_children():
            self.box.remove(i)

        self.top_bar.enable_prev()
        self.top_bar.disable_next()

        home.goto(None, None, self.last_level_visited)
        self.show_all()


def main():

    # Create style sheet
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_path('style.css')
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    win = MainWindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
