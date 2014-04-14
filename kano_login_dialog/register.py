#!/usr/bin/env python

# register.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for register screen

from gi.repository import Gtk

from components import heading, green_button
from kano.world import register_profile


def activate(_win, _box):
    email_entry = Gtk.Entry()
    username_entry = Gtk.Entry()
    password_entry = Gtk.Entry()

    title = heading.Heading("Register", "Become a real person")

    email_entry.props.placeholder_text = "Email"
    username_entry.props.placeholder_text = "Username"
    password_entry.props.placeholder_text = "Password"
    password_entry.set_visibility(False)

    register = green_button.Button("REGISTER")
    register.button.connect("button_press_event", register_user, email_entry, username_entry, password_entry, _win)

    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    container.pack_start(email_entry, False, False, 0)
    container.pack_start(username_entry, False, False, 0)
    container.pack_start(password_entry, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0.3, xscale=0, yscale=0)
    #padding_above = 0
    #valign.set_padding(padding_above, 0, 0, 0)
    valign.add(container)
    _box.pack_start(title.container, False, False, 0)
    _box.pack_start(valign, False, False, 0)
    _box.pack_start(register.box, False, False, 15)


def register_user(button, event, email_entry, username_entry, password_entry, win):
    email_text = email_entry.get_text()
    username_text = username_entry.get_text()
    password_text = password_entry.get_text()
    print 'email = {0} , username = {1} , password = {2}'.format(email_text, username_text, password_text)

    success, text = register_profile(email_text, username_text, password_text)

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

    else:
        dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "Registered!")
        dialog.format_secondary_text("Activate your account - check " + text + " for an email")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
        else:
            dialog.destroy()


