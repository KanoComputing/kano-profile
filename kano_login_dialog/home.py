#!/usr/bin/env python

# home.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for home screen.  User can choose to login or register from here

from gi.repository import Gtk

from . import login, register
from components import heading, green_button

win = None
box = None


def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    for i in _box.get_children():
        _box.remove(i)

    title = heading.Heading("Hello!", "Do you already have an account?")

    loginB = green_button.Button("Yes! Let me log in")
    loginB.button.set_size_request(200, 44)

    registerB = green_button.Button("I want to create a new account")
    registerB.button.set_size_request(300, 44)

    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    container.pack_start(loginB.box, False, False, 10)
    container.pack_start(registerB.box, False, False, 10)

    valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    padding_above = 20
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(container)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(valign, False, False, 0)

    # Connect button to screens
    loginB.button.connect("button_press_event", goto, 'login')
    registerB.button.connect("button_press_event", goto, 'register')


def goto(button, event, page):
    global win, box

    refs = {
        'login': login,
        'register': register,
    }

    module = refs[page]

    for i in box.get_children():
        box.remove(i)

    win.top_bar.enable_prev()
    win.top_bar.disable_next()

    win.last_level_visited = page

    module.activate(win, box)
    win.show_all()
