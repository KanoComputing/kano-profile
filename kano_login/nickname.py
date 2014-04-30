#!/usr/bin/env python

# nickname.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set nickname of user

from gi.repository import Gtk

from components import heading, green_button
from kano_login import gender

win = None
box = None
username = None


def activate(_win, _box):
    global win, box, username

    win = _win
    box = _box

    win.clear_box()

    nickname_entry = Gtk.Entry()
    nickname_entry.set_placeholder_text("Type your nickname here")
    title = heading.Heading("Nickname", "What do you want us to call you?")

    valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=1)
    padding = 10
    valign.set_padding(padding, padding, 0, 0)

    next_button = green_button.Button("NEXT")
    next_button.button.connect("button_press_event", set_nickname, username)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(nickname_entry, False, False, 30)
    box.pack_start(next_button.box, False, False, 0)
    box.show_all()

    username = nickname_entry.get_text()


def set_nickname(arg1=None, arg2=None, username=""):
    print "setting nickname"
    win.nickname = username
    gender.activate(win, box)
