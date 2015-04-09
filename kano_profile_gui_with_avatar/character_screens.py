#!/usr/bin/env python

# character_screen.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
from gi.repository import Gtk
from kano_profile_gui_with_avatar.progress_bar import ProgressBar
from kano_avatar_gui.CharacterCreator import CharacterCreator
from kano.gtk3.buttons import KanoButton, OrangeButton


class CharacterScreenDisplay(Gtk.EventBox):
    '''Show the character created by the user, progress bar,
    and button with option to edit.
    The window passed/template we're using should already
    have the top bar in it.  The main thing we need to do is
    set the selected item to the correct one.
    '''

    def __init__(self, win):
        Gtk.EventBox.__init__(self)

        self._win = win

        # Pack this part of the screen into the window
        self._win.pack_widget(self)
        self._char_creator = self._win.get_char_creator()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Get the image from the character creator, and then display it
        self._progress = ProgressBar(self.width)

        vbox.pack_start(self._char_creator, False, False, 0)
        vbox.pack_start(self._progress, False, False, 0)

        self._win.show_all()

    def go_to_edit_character_screen(self):
        CharacterScreenEdit(self._win)


class CharacterScreenEdit(Gtk.EventBox):
    '''Offer the user the option to modify their avatar
    '''

    def __init__(self, win):
        Gtk.EventBox.__init__(self)

        self._win = win
        self._win.pack_widget(self)

        # Should this be inherited, passed as a variable, or global?
        # Could be a member variable in window.
        self.char_creator = self._win.get_char_creator()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        save_changes_button = KanoButton("SAVE CHANGES")
        save_changes_button.connect("clicked", self.save_changes)

        discard_changes_button = OrangeButton("DISCARD")
        discard_changes_button.connect("clicked", self.save_changes)
        empty_label = Gtk.Label("")

        button_box = Gtk.ButtonBox()
        button_box.pack_start(discard_changes_button, False, False, 0)
        button_box.pack_start(save_changes_button, False, False, 0)
        button_box.pack_start(empty_label, False, False, 0)

        vbox.pack_start(self.char_creator, False, False, 0)
        vbox.pack_start(button_box, False, False, 0)

        self._win.show_all()

    def save_changes(self, widget):
        self.char_creator.save()

    def discard_changes(self):
        '''Don't save, just go back to the edit character screen
        '''
        CharacterScreenDisplay(self._win)
