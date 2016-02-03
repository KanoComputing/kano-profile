# TermsAndConditions.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


from gi.repository import GObject, Gtk

from kano.gtk3.buttons import OrangeButton


class TermsAndConditions(Gtk.Box):
    __gsignals__ = {
        't-and-cs-clicked': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def __init__(self):
        Gtk.Box.__init__(self)

        self.checkbutton = Gtk.CheckButton()
        self.checkbutton.get_style_context().add_class("get_data_checkbutton")
        self.checkbutton.set_margin_left(30)

        self.tc_button = OrangeButton(_("I agree to the terms and conditions"))
        self.tc_button.connect("clicked", self._emit_t_and_c_signal)

        self.pack_start(self.checkbutton, False, False, 0)
        self.pack_start(self.tc_button, False, False, 0)

    def is_checked(self):
        return self.checkbutton.get_active()

    def _emit_t_and_c_signal(self, widget):
        self.emit("t-and-cs-clicked")

    def disable_all(self):
        self.checkbutton.set_sensitive(False)
        self.tc_button.set_sensitive(False)

    def enable_all(self):
        self.checkbutton.set_sensitive(True)
        self.tc_button.set_sensitive(True)
