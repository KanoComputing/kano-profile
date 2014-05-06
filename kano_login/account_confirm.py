#!/usr/bin/env python

# account_confirm.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for confirming to the user they've registered

from gi.repository import Gtk
from components import heading, green_button

win = None
box = None


def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    win.clear_box()

    if win.age < 13:
        nextB = Gtk.Button("GOT IT")
        nextB.get_style_context().add_class("green_button")

        title = heading.Heading("Confirmation email", "An email has been sent to:")

        label1 = Gtk.Label(win.email)
        label1.get_style_context().add_class()

        label2 = Gtk.Label("This needs to be confirmed sometime")

        label_container = Gtk.Grid(column_homogeneous=False,
                                   row_spacing=7)
        label_container.attach(label1, 0, 0, 1, 1)
        label_container.attach(label2, 0, 1, 1, 1)

        valign = Gtk.Alignment()
        valign.add(label_container)
        valign.set_padding(0, 0, 100, 0)
        box.pack_start(title.container, False, False, 0)
        box.pack_start(valign, False, False, 0)
        box.pack_start(nextB, False, False, 15)
        box.show_all()
    else:
        confirmation_screen()


def confirmation_screen():
    global win, box

    win.clear_box()

    doneB = green_button.Button("DONE")
    doneB.button.connect("button_press_event", finish)

    title = heading.Heading("Profile created!", "Boom")

    box.pack_start(title.container, False, False, 0)
    box.pack_start(doneB.box, False, False, 15)
    box.show_all()


def go_next(button, event, entry1):
    confirmation_screen()


def finish(button, event):
    Gtk.main_quit()
