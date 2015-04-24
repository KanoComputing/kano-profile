#!/usr/bin/env python

# LabelledEntry.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, GObject


class LabelledEntry(Gtk.Box):
    '''Produces a labelled entry, suitable for the registration screens
    '''
    __gsignals__ = {
        'labelled-entry-key-release': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, text, entry_contents=None):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self._label = Gtk.Label(text, xalign=0)
        self._label.get_style_context().add_class("get_data_label")
        self.pack_start(self._label, False, False, 0)

        self._entry = Gtk.Entry()
        self._entry.get_style_context().add_class("get_data_entry")
        self._entry.set_size_request(200, -1)

        if entry_contents:
            self._entry.set_text(entry_contents)

        self.pack_start(self._entry, False, False, 10)
        self._entry.connect("key-release-event", self.emit_signal)

        self.set_margin_right(80)
        self.set_margin_left(30)

    def set_visibility(self, value):
        return self._entry.set_visibility(value)

    def get_text(self):
        return self._entry.get_text()

    def set_text(self, text):
        self._entry.set_text(text)

    def emit_signal(self, widget, event):
        self.emit('labelled-entry-key-release')

    def get_label_text(self):
        return self._label.get_text()
