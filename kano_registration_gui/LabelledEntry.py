#!/usr/bin/env python

# LabelledEntry.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, GObject
from kano_registration_gui.ValidationEntry import ValidationEntry


class LabelledEntry(Gtk.Box):
    '''Produces a labelled entry, suitable for the registration screens
    '''
    __gsignals__ = {
        'labelled-entry-key-release': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self, text, entry_contents=None):

        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # This is for the two labels above the entry
        # One is information about the entry information
        # The other is about whether the information is valid
        label_hbox = Gtk.Box()
        self._title_label = Gtk.Label(text, xalign=0)
        self._title_label.get_style_context().add_class("get_data_label")

        self._validated = False

        self._validation_label = Gtk.Label()
        self._validation_label.get_style_context().add_class("validation_label")
        label_hbox.pack_start(self._title_label, False, False, 0)
        label_hbox.pack_start(self._validation_label, False, False, 0)
        self.pack_start(label_hbox, False, False, 0)

        self._entry = ValidationEntry()
        self._entry.get_style_context().add_class("get_data_entry")
        self._entry.set_size_request(250, -1)

        if entry_contents:
            self._entry.set_text(entry_contents)

        self.pack_start(self._entry, False, False, 0)
        self._entry.connect("key-release-event", self.emit_signal)

        self.set_margin_right(30)
        self.set_margin_left(30)

    @property
    def validated(self):
        '''How we find out whether the entry is validated
        '''
        return self._validated

    # This is a public function
    def label_success(self, text="", successful=None):
        '''successful is "success", "fail" or None
        If success, turn validation label green
        Fail turns it red
        Otherwise, don't show it.
        '''
        self._validation_label.get_style_context().remove_class("fail")
        self._validation_label.get_style_context().remove_class("success")

        # Change the image - if successful is nothing, then icon
        # is removed
        self.set_image(successful)

        # If successful is not nothing, set the class appropriately
        if successful:
            self._validation_label.get_style_context().add_class(successful)
            self._validation_label.set_text(text)
            self._validated = (successful == "success")

        self._validation_label.show_all()

    def set_image(self, name):
        self._entry.set_image(name)

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
