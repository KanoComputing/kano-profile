#!/usr/bin/env python

# register.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for register screen

from gi.repository import Gtk

from kano.logging import logger
from kano.gtk3.heading import Heading
from kano.gtk3.buttons import KanoButton, OrangeButton
from kano.utils import run_bg
from kano_profile.paths import bin_dir, legal_dir
from kano_profile.profile import save_profile_variable
from kano_world.functions import register as register_
from kano.gtk3 import kano_dialog
from kano_login.labelled_entries import LabelledEntries
import re
import os
import sys

win = None
box = None
over_13 = True


def is_email(email):
    pattern = '[\.\w]{1,}[@]\w+[.]\w+'
    if re.match(pattern, email):
        return True
    else:
        return False


# We calculate age based on the birthday screen - if less than 13,
# we ask for parent's email
def activate(_win, _box, _over_13=True):
    global win, box, over_13

    win = _win
    box = _box
    over_13 = _over_13

    header = "Login details"
    subheading = ""

    if over_13:
        subheading = "Pick a cool name, add an email and set a password"
        entries_container = LabelledEntries([{"heading": "Username", "subheading": ""}, {"heading": "Email", "subheading": ""}, {"heading": "Password", "subheading": ""}])
    else:
        subheading = "Pick a cool name and a secret password"
        entries_container = LabelledEntries([{"heading": "Username", "subheading": ""}, {"heading": "Password", "subheading": ""}])

    title = Heading(header, subheading)

    go_to_terms_conditions = OrangeButton("I accept the terms and conditions")
    checkbutton = Gtk.CheckButton()
    checkbox_box = Gtk.Box()
    checkbox_box.pack_start(checkbutton, False, False, 0)
    checkbox_box.pack_start(go_to_terms_conditions, False, False, 0)
    checkbox_align = Gtk.Alignment(xscale=0, xalign=0.5)
    checkbox_align.add(checkbox_box)

    register = KanoButton("REGISTER")
    register.pack_and_align()
    register.set_padding(0, 10, 0, 0)
    register.set_sensitive(False)

    entries = entries_container.get_entries()

    for entry in entries:
        entry.connect("key_release_event", set_sensitive_on_key_up, entries_container, register, checkbutton)

    checkbutton.connect("toggled", set_sensitive_toggled, entries_container, register, checkbutton)
    register.connect("button-press-event", register_user, entries)
    register.connect("key-press-event", register_user, entries)
    go_to_terms_conditions.connect("button_press_event", show_terms_and_conditions, checkbutton)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(entries_container, False, False, 5)
    box.pack_start(checkbox_align, False, False, 5)
    box.pack_start(register.align, False, False, 5)
    box.show_all()


def show_terms_and_conditions(widget, event, checkbutton):
    checkbutton.set_active(True)

    legal_text = ''
    for file in os.listdir(legal_dir):
        with open(legal_dir + file, 'r') as f:
            legal_text = legal_text + f.read() + '\n\n\n'

    kdialog = kano_dialog.KanoDialog("Terms and conditions", "", scrolled_text=legal_text)
    kdialog.run()


def set_register_sensitive(entries_container, button, checkbutton):
    entry_text = entries_container.get_entry_text()
    text1 = entry_text[1]
    text2 = entry_text[2]
    text3 = entry_text[3]
    bool_value = checkbutton.get_active()
    if text1 != "" and text2 != "" and text3 != "" and bool_value:
        button.set_sensitive(True)
    else:
        button.set_sensitive(False)


def set_sensitive_toggled(widget, entries_container, button, checkbutton):
    set_register_sensitive(entries_container, button, checkbutton)


def set_sensitive_on_key_up(widget, event, entries_container, button, checkbutton):
    set_register_sensitive(entries_container, button, checkbutton)


def register_user(button, event, entries):
    global win

    if not hasattr(event, 'keyval') or event.keyval == 65293:

        win.username = entries[0].get_text()

        if over_13:
            win.email = entries[1].get_text()
            win.password = entries[2].get_text()
        else:
            win.password = entries[1].get_text()

        logger.info('trying to register user')
        success, text = register_(win.email, win.username, win.password)

        if not success:
            logger.info('problem with registration: {}'.format(text))
            kdialog = kano_dialog.KanoDialog("Houston, we have a problem", str(text))
            kdialog.run()

        else:
            logger.info('registration successful')

            save_profile_variable('gender', win.gender)
            save_profile_variable('birthdate', win.date)

            # running kano-sync after registration
            logger.info('running kano-sync after successful registration')
            cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            run_bg(cmd)

            win.update()

            #close window
            sys.exit(0)

