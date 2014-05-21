#!/usr/bin/env python

# register.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for register screen

from gi.repository import Gtk

from components import heading, green_button, kano_dialog, cursor
from kano.utils import run_bg
from kano.profile.paths import bin_dir
from kano.profile.profile import save_profile_variable
from kano.world.functions import register as register_
from kano_login import account_confirm
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
    username_entry = Gtk.Entry()
    email_entry = Gtk.Entry()
    password_entry = Gtk.Entry()

    go_to_terms_conditions = Gtk.Button("I accept the terms and conditions")
    go_to_terms_conditions.connect("button_press_event", show_terms_and_conditions)
    cursor.attach_cursor_events(go_to_terms_conditions)
    # TODO: change this class
    go_to_terms_conditions.get_style_context().add_class("not_registered")
    checkbutton = Gtk.CheckButton()
    checkbox_box = Gtk.Box()
    checkbox_box.pack_start(checkbutton, False, False, 0)
    checkbox_box.pack_start(go_to_terms_conditions, False, False, 0)
    checkbox_align = Gtk.Alignment(xscale=0, xalign=0.5)
    checkbox_align.add(checkbox_box)

    register = green_button.Button("REGISTER")
    register.button.set_sensitive(False)

    username_entry.connect("key_release_event", set_sensitive_on_key_up, email_entry, username_entry, password_entry, register.button, checkbutton)
    email_entry.connect("key_release_event", set_sensitive_on_key_up, email_entry, username_entry, password_entry, register.button, checkbutton)
    password_entry.connect("key_release_event", set_sensitive_on_key_up, email_entry, username_entry, password_entry, register.button, checkbutton)
    checkbutton.connect("toggled", set_sensitive_toggled, email_entry, username_entry, password_entry, register.button, checkbutton)
    register.button.connect("button-press-event", register_user, username_entry, email_entry, password_entry)

    subheading = ''
    if win.age < 13:
        header = "Permission slip"
        subheading = "Please provide a parent's or teacher's email"
    else:
        header = "Login details"
        subheading = "Become a real person"

    title = heading.Heading(header, subheading)

    username_entry.set_placeholder_text("Username")
    email_entry.set_placeholder_text("Email")
    password_entry.set_placeholder_text("Password")
    password_entry.set_visibility(False)

    entry_container = Gtk.Grid(column_homogeneous=False,
                               row_spacing=7)
    entry_container.attach(username_entry, 0, 0, 1, 1)
    entry_container.attach(email_entry, 0, 1, 1, 1)
    entry_container.attach(password_entry, 0, 2, 1, 1)

    valign = Gtk.Alignment()
    valign.add(entry_container)
    valign.set_padding(0, 0, 100, 0)
    box.pack_start(title.container, False, False, 0)
    box.pack_start(valign, False, False, 0)
    box.pack_start(checkbox_align, False, False, 2)
    box.pack_start(register.align, False, False, 5)
    box.show_all()


def show_terms_and_conditions(widget, event):
    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolledwindow.set_size_request(400, 200)
    lots_of_text = Gtk.TextView()
    lots_of_text.get_buffer().set_text("Blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah blah blah blah blah blah blah"
                                       "blah blah blah blah blah blah blah blah")
    lots_of_text.set_wrap_mode(Gtk.WrapMode.WORD)
    lots_of_text.set_editable(False)
    scrolledwindow.add(lots_of_text)
    kano_dialog.KanoDialog("Terms and conditions", "", None, scrolledwindow)


def set_register_sensitive(entry1, entry2, entry3, button, checkbutton):
    text1 = entry1.get_text()
    text2 = entry2.get_text()
    text3 = entry3.get_text()
    bool_value = checkbutton.get_active()
    if text1 != "" and text2 != "" and text3 != "" and bool_value:
        button.set_sensitive(True)
    else:
        button.set_sensitive(False)


def set_sensitive_toggled(widget, entry1, entry2, entry3, button, checkbutton):
    set_register_sensitive(entry1, entry2, entry3, button, checkbutton)


def set_sensitive_on_key_up(widget, event, entry1, entry2, entry3, button, checkbutton):
    set_register_sensitive(entry1, entry2, entry3, button, checkbutton)


def register_user(button, event, username_entry, email_entry, password_entry):
    global win

    win.email = email_entry.get_text()
    win.username = username_entry.get_text()
    win.password = password_entry.get_text()

    success, text = register_(win.email, win.username, win.password)

    if not success:
        kano_dialog.KanoDialog("Houston, we have a problem", str(text))

    # This needs to be adjusted depending on the age of the user
    else:
        save_profile_variable('gender', win.gender)
        save_profile_variable('age', win.age)

        # sync on each successfule login/restore
        cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
        run_bg(cmd)

        win.update()
        account_confirm.activate(win, box)


