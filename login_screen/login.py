#!/usr/bin/env python

# login.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for login screen

from gi.repository import Gtk
import components.heading as heading
import components.green_button as green_button


def activate(_win, _box):
    username_entry = Gtk.Entry()
    password_entry = Gtk.Entry()

    title = heading.Heading("Log in", "Open up your world")

    username_entry.props.placeholder_text = "Username"
    password_entry.props.placeholder_text = "Password"
    password_entry.set_visibility(False)

    login = green_button.Button("LOG IN")
    login.button.connect("button_press_event", log_user_in, username_entry, password_entry)

    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    container.pack_start(username_entry, False, False, 0)
    container.pack_start(password_entry, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
    padding_above = 10
    valign.set_padding(padding_above, 0, 0, 0)
    valign.add(container)
    _box.pack_start(title.container, False, False, 0)
    _box.pack_start(valign, False, False, 0)
    _box.pack_start(login.box, False, False, 30)


def log_user_in(button, event, username_entry, password_entry):
    username_text = username_entry.get_text()
    password_text = password_entry.get_text()
    print 'username = {0} , password = {1}'.format(username_text, password_text)
