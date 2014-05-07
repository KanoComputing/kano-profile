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
        nextB = green_button.Button("GOT IT")
        nextB.button.connect("button_press_event", confirmation_screen)

        title = heading.Heading("Now get your parents to confirm...", "An email has been sent to: ")

        label1 = Gtk.Label(win.email)
        label1.get_style_context().add_class("confirm_email")

        # Done by eye
        label1.set_alignment(0.5, 0)

        label2 = Gtk.Label("Bug them to check their email in the next 14 days - \n                         or you'll lose your profile!")
        label2.get_style_context().add_class("confirm_email_info")
        label2.set_alignment(0.5, 0)

        box.pack_start(title.container, False, False, 0)
        box.pack_start(label1, False, False, 5)
        box.pack_start(label2, False, False, 20)
        box.pack_start(nextB.box, False, False, 15)
        box.show_all()
    else:
        confirmation_screen()


def confirmation_screen(widget=None, event=None):
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
