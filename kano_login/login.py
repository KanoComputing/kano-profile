#!/usr/bin/env python

# login.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for login screen

from gi.repository import Gtk

from components import heading, green_button
from kano.utils import run_bg
from kano.profile.paths import bin_dir
from kano.profile.profile import load_profile, save_profile_variable
from kano.world.functions import login as login_, is_registered
from kano_login import gender

win = None
box = None

profile = load_profile()
force_login = is_registered() and 'kanoworld_username' in profile


def activate(_win, _box):
    global win, box

    win = _win
    box = _box
    password_entry = Gtk.Entry()

    title = heading.Heading("Log in", "Open up your world")

    if force_login:
        username = profile['kanoworld_username']
        username_email_forced = Gtk.Label(username)
        username_email_forced_style = username_email_forced.get_style_context()
        username_email_forced_style.add_class('description')
    else:
        username_email_entry = Gtk.Entry()
        username_email_entry.props.placeholder_text = 'Username or email'

    password_entry.props.placeholder_text = 'Password'
    password_entry.set_visibility(False)

    login = green_button.Button("LOG IN")
    if force_login:
        login.button.connect("button_press_event", log_user_in, None, password_entry, username, _win)
    else:
        login.button.connect("button_press_event", log_user_in, username_email_entry, password_entry, None, _win)
    login.set_padding(10, 0, 0, 0)

    if not force_login:
        not_registered = Gtk.Button("Not registered?")
        not_registered.get_style_context().add_class("not_registered")
        not_registered.connect("clicked", register)

    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    if force_login:
        container.pack_start(username_email_forced, False, False, 0)
    else:
        container.pack_start(username_email_entry, False, False, 0)
    container.pack_start(password_entry, False, False, 0)

    valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=1)
    padding = 10
    valign.set_padding(padding, padding, 0, 0)
    valign.add(container)

    _box.pack_start(title.container, False, False, 0)
    _box.pack_start(valign, False, False, 0)
    _box.pack_start(login.align, False, False, 10)

    if not force_login:
        _box.pack_start(not_registered, False, False, 0)

    _win.show_all()


def register(event):
    global win, box

    win.update()
    gender.activate(win, box)


def log_user_in(button, event, username_email_entry, password_entry, username_email, win):
    if username_email_entry:
        username_email = username_email_entry.get_text()
    password_text = password_entry.get_text()

    success, text = login_(username_email, password_text)

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
        # restore on first successful login/restore
        first_run_done = False
        try:
            first_run_done = profile['first_run_done']
        except Exception:
            pass

        if not first_run_done:
            print 'doing first time restore'
            cmd = '{bin_dir}/kano-sync --sync --restore -s'.format(bin_dir=bin_dir)
            run_bg(cmd)
            save_profile_variable('first_run_done', True)
        else:
            # sync on each successfule login/restore
            cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
            run_bg(cmd)

        dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "Logged in!")
        dialog.format_secondary_text("Yay!")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.destroy()
            Gtk.main_quit()
        else:
            dialog.destroy()
            Gtk.main_quit()

