#!/usr/bin/env python

# first_screen.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# First screen of profile on first run
# Launched on straight after kano-settings
# Dependent on internet connection


from gi.repository import Gtk

from components import heading, green_button
from kano_login import nickname
from kano.network import is_internet

win = None
box = None


def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    win.clear_box()

    if is_internet():
        title = heading.Heading("You've made some progress, let's save it!", "Lets create an account")
        next_button = green_button.Button("NEXT")
        next_button.button.connect("button_press_event", update)
        box.pack_start(title.container, False, False, 0)
        box.pack_start(next_button.box, False, False, 0)
    else:
        title = heading.Heading("You should get an account, but you need internet!", "Come back later")
        done_button = green_button.Button("DONE")
        done_button.button.connect("button_press_event", close_window)
        box.pack_start(title.container, False, False, 0)
        box.pack_start(done_button.box, False, False, 0)

    box.show_all()


def update(widget, event):
    global win, box

    nickname.activate(win, box)
    win.state = win.state + 1


def close_window(widget, event):
    Gtk.main_quit()
