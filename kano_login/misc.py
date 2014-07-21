#!/usr/bin/env python

# about_you.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Create custom label and add the label to any widget

from gi.repository import Gtk


def add_heading(text, widget, bold=False):

    label = Gtk.Label(text)
    label_alignment = Gtk.Alignment(xscale=0, xalign=0)
    label_alignment.add(label)

    if bold:
        label.get_style_context().add_class("bold_label")
    else:
        label.get_style_context().add_class("desc_label")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.pack_start(label_alignment, False, False, 3)
    box.pack_start(widget, False, False, 3)

    return box


def create_custom_label(heading, description=""):

    heading_label = Gtk.Label(heading)
    heading_label.get_style_context().add_class("bold_label")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.pack_start(heading_label, False, False, 0)

    if description:
        description_label = Gtk.Label(description)
        description_label.get_style_context().add_class("desc_label")
        box.pack_start(description_label, False, False, 0)

    align = Gtk.Alignment(yscale=0, yalign=0.5)
    align.add(box)

    return align


def create_labelled_widget(heading, description="", widget=None):

    label_box = create_custom_label(heading, description)
    box = Gtk.Box()
    box.pack_start(label_box, False, False, 5)
    box.pack_start(widget, False, False, 5)

    align = Gtk.Alignment(xscale=0, xalign=1)
    align.add(box)

    return align
