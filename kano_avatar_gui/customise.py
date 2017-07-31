#
# customise.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Open a kano-profile wardrobe screen in edit mode
#

from gi.repository import Gtk, GLib

from kano_avatar_gui.CharacterCreator import CharacterCreator
from kano.gtk3.buttons import KanoButton


class CharacterWindow(Gtk.Window):
    def __init__(self, cb):
        super(CharacterWindow, self).__init__()
        self.get_style_context().add_class("character_window")
        self.set_decorated(False)
        self.close_cb = cb

        self.char_edit = CharacterCreator(randomise=True, no_sync=True)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(self.char_edit, False, False, 0)
        button = KanoButton(_("OK"))
        button.connect("clicked", self.close_window)
        button.pack_and_align()

        self.connect("delete-event", Gtk.main_quit)
        self.set_keep_above(True)

        vbox.pack_start(button.align, False, False, 10)
        self.show_all()

    def close_window(self, dummy_widget):
        self.char_edit.save()
        self.destroy()
        GLib.idle_add(self.close_cb)


def clean_up():
    Gtk.main_quit()


def show_wardrobe():
    win = CharacterWindow(clean_up)
    win.show_all()
    win.char_edit.select_category_button('judoka-suits')

    return win
