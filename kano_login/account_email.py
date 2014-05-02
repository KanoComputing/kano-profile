#!/usr/bin/env python

# account_email.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for registering email

from gi.repository import Gtk

from components import heading, green_button
#from kano.world.functions import register as register_
import re
from kano_login import account_password

win = None


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


# We calclate age based on the birthday screen - if less than 13,
# we ask for parent's email
def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    win.clear_box()
    email_entry1 = Gtk.Entry()
    email_entry2 = Gtk.Entry()

    nextB = green_button.Button("NEXT")

    email_entry1.connect("key_release_event", unlock_second_entry, email_entry2, nextB.button)
    email_entry2.set_sensitive(False)
    email_entry2.connect("key_release_event", set_next_button, email_entry1, nextB.button)
    nextB.button.connect("button_press_event", register_email, email_entry1)
    nextB.button.set_sensitive(False)

    subheading = ''
    if win.age < 13:
        subheading = "Please provide a parent's email"
    else:
        subheading = "Become a real person"

    title = heading.Heading("Register your email", subheading)

    email_entry1.set_placeholder_text("Email")
    email_entry2.set_placeholder_text("Confirm your email")

    entry_container = Gtk.Grid(column_homogeneous=False,
                               row_spacing=7)
    entry_container.attach(email_entry1, 0, 0, 1, 1)
    entry_container.attach(email_entry2, 0, 1, 1, 1)

    valign = Gtk.Alignment()
    valign.add(entry_container)
    valign.set_padding(0, 0, 100, 0)
    box.pack_start(title.container, False, False, 0)
    box.pack_start(valign, False, False, 0)
    box.pack_start(nextB.box, False, False, 15)
    box.show_all()


def check_match(widget, event, entry1, entry2):
    text1 = entry1.get_text()
    text2 = entry2.get_text()

    if text1 == text2 and text1 != "":
        return True
    else:
        return False


def unlock_second_entry(entry1, event, entry2, button):
    if is_email(entry1.get_text()):
        entry2.set_sensitive(True)
    else:
        entry2.set_sensitive(False)
        button.set_sensitive(False)


def set_next_button(entry2, event, entry1, button):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    if text1 != "" and text1 == text2:
        button.set_sensitive(True)
    else:
        button.set_sensitive(False)


def register_email(button, widget, entry1):
    global win, box

    win.email = entry1.get_text()
    account_password.activate(win, win.box)

    win.state = win.state + 1


