#!/usr/bin/env python

# account_password.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for registering password

from gi.repository import Gtk

from components import heading, green_button
from kano.world.functions import register as register_
from kano_login import account_confirm

win = None
box = None


def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    win.clear_box()
    entry1 = Gtk.Entry()
    entry2 = Gtk.Entry()

    nextB = green_button.Button("REGISTER")

    entry1.connect("key_release_event", set_next_button, entry2, nextB.button)
    entry1.set_visibility(False)
    entry2.connect("key_release_event", set_next_button, entry1, nextB.button)
    entry2.set_visibility(False)
    nextB.button.connect("button_press_event", register_user, entry1)
    nextB.button.set_sensitive(False)

    title = heading.Heading("Create your password", "Make it hard to guess")

    entry1.set_placeholder_text("Password")
    entry2.set_placeholder_text("Confirm your password")

    entry_container = Gtk.Grid(column_homogeneous=False,
                               row_spacing=7)
    entry_container.attach(entry1, 0, 0, 1, 1)
    entry_container.attach(entry2, 0, 1, 1, 1)

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


def set_next_button(entry2, event, entry1, button):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    if text1 != "" and text1 == text2:
        button.set_sensitive(True)
    else:
        button.set_sensitive(False)


def register_user(button, event, password_entry):
    global win, box

    email_text = win.email
    #username_text = username_entry.get_text()
    username_text = win.username
    password_text = password_entry.get_text()

    print 'email = {0} , username = {1} , password = {2}'.format(email_text, username_text, password_text)

    success, text = register_(email_text, username_text, password_text)

    if not success:
        print "error = " + str(text)
        dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK, "Houston, we have a problem")
        dialog.format_secondary_text(text)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
        else:
            dialog.destroy()

    # This needs to be adjusted depending on the age of the user
    else:
        dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "Registered!")
        dialog.format_secondary_text("Activate your account - check " + text + " for an email")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
        else:
            dialog.destroy()

    account_confirm.activate(win, box)
    win.state = win.state + 1
