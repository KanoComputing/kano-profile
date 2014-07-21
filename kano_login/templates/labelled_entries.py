#!/usr/bin/env python

# labelled_entries.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Template for creating a list of labelled entries

from gi.repository import Gtk
from kano_login.misc import create_labelled_widget


class LabelledEntries(Gtk.Alignment):

    def __init__(self, entries_info):
        Gtk.Alignment.__init__(self)
        self.set_padding(0, 0, 0, 100)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.entries = []

        # entries_info = [{"heading": "", "subheading": ""}, {"heading": "", "subheading": ""}]
        for info in entries_info:
            entry = Gtk.Entry()
            align = create_labelled_widget(info["heading"], info["subheading"], entry)
            self.entries.append(entry)
            self.box.pack_start(align, False, False, 5)

        self.add(self.box)

    def get_entries(self):
        return self.entries

    def get_entry(self, number):
        return self.entries[number]

    def get_entry_text(self):
        all_text = []

        for entry in self.entries:
            text = entry.get_text()
            all_text.append(text)

        return all_text

    def set_spacing(self, number):
        self.box.set_spacing(number)

