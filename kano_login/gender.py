#!/usr/bin/env python

# gender.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Set nickname of user

from gi.repository import Gtk

from components import heading, green_button
from kano_login import birthday

win = None
box = None


def activate(_win, _box):
    global win, box

    win = _win
    box = _box

    win.clear_box()

    print "activating gender"

    #gender_list = Gtk.ListStore(int, str)
    #gender_list.append([1, "Girl"])
    #gender_list.append([2, "Boy"])
    #gender_combo = Gtk.ComboBox.new_with_model_and_entry(gender_list)

    gender_combo = Gtk.ComboBoxText()
    gender_combo.append_text("Girl")
    gender_combo.append_text("Boy")
    gender_combo.connect("changed", on_gender_combo_changed)
    gender_combo.get_style_context().add_class("gender_dropdown_list")

    title = heading.Heading("Gender", "Are you a boy or girl?")

    valign = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=1)
    padding = 10
    valign.set_padding(padding, padding, 0, 0)

    next_button = green_button.Button("NEXT")
    next_button.button.connect("button_press_event", set_gender, gender_combo)

    box.pack_start(title.container, False, False, 0)
    box.pack_start(gender_combo, False, False, 30)
    box.pack_start(next_button.box, False, False, 0)
    box.show_all()


def on_gender_combo_changed(arg1=None, arg2=None):
    print "changing gender"


def set_gender(arg1=None, arg2=None, gender_combo=None):
    print "setting gender"
    active_iter = gender_combo.get_active_text()
    print active_iter
    birthday.activate(win, box)
