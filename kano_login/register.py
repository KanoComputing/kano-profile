#!/usr/bin/env python

# register.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for register screen

from gi.repository import Gtk

from components import heading
from kano.world.functions import register as register_
import re
#from kano_login import home, login,

win = None
box = None


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
    password_entry1 = Gtk.Entry()
    password_entry2 = Gtk.Entry()

    register = Gtk.Button("REGISTER")
    register.get_style_context().add_class("green_button")

    email_entry1.connect("key_release_event", unlock_second_entry, email_entry2, register)
    email_entry2.connect("key_release_event", set_email_icon, email_entry1, password_entry1, password_entry2, register)
    email_entry2.set_sensitive(False)
    password_entry1.connect("key_release_event", set_register_button, password_entry2, register)
    password_entry1.set_sensitive(False)
    password_entry2.connect("key_release_event", set_register_button, password_entry1, register)
    password_entry2.set_sensitive(False)
    register.connect("button_press_event", register_user, email_entry1, password_entry1, _win)
    register.set_sensitive(False)

    subheading = ''
    if win.age < 13:
        subheading = "Please provide a parent's email"
    else:
        subheading = "Become a real person"

    title = heading.Heading("Register", subheading)

    email_entry1.set_placeholder_text("Email")
    email_entry2.set_placeholder_text("Confirm your email")
    password_entry1.set_placeholder_text("Password")
    password_entry1.set_visibility(False)
    password_entry2.set_placeholder_text("Confirm your password")
    password_entry2.set_visibility(False)

    entry_container = Gtk.Grid(column_homogeneous=False,
                               row_spacing=7)
    entry_container.attach(email_entry1, 0, 0, 1, 1)
    entry_container.attach(email_entry2, 0, 1, 1, 1)
    entry_container.attach(password_entry1, 0, 2, 1, 1)
    entry_container.attach(password_entry2, 0, 3, 1, 1)

    valign = Gtk.Alignment()
    valign.add(entry_container)
    valign.set_padding(0, 0, 100, 0)
    box.pack_start(title.container, False, False, 0)
    box.pack_start(valign, False, False, 0)
    box.pack_start(register, False, False, 15)
    box.show_all()


def check_match(widget, event, entry1, entry2):
    text1 = entry1.get_text()
    text2 = entry2.get_text()

    if text1 == text2:
        return True
    else:
        return False


def unlock_second_entry(entry1, event, entry2, button):
    if is_email(entry1.get_text()):
        entry2.set_sensitive(True)
    else:
        entry2.set_sensitive(False)
        button.set_sensitive(False)


def set_email_icon(entry2, event, entry1, entry3, entry4, button):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    if text1 == text2:
        entry3.set_sensitive(True)
        entry4.set_sensitive(True)
    else:
        entry3.set_sensitive(False)
        entry4.set_sensitive(False)
        button.set_sensitive(False)


def set_register_button(entry2, event, entry1, button):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    if text1 != "" and text1 == text2:
        button.set_sensitive(True)
    else:
        button.set_sensitive(False)


def update_register_button(widget, event, entry1, entry2, entry3, entry4, button):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    text3 = entry3.get_text()
    text4 = entry4.get_text()
    if text1 != "" and text2 != "" and text3 != "" and text4 != "":
        if check_match(None, None, entry1, entry2) and check_match(None, None, entry3, entry4):
            button.set_sensitive(True)


def register_user(button, event, email_entry, password_entry, win):
    email_text = email_entry.get_text()
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


