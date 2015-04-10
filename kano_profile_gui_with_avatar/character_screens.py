#!/usr/bin/env python

# character_screen.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
from gi.repository import Gtk
from kano_profile_gui_with_avatar.progress_bar import ProgressBar
from kano.gtk3.buttons import KanoButton, OrangeButton


class CharacterDisplay(Gtk.EventBox):
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
        self._char_creator = self._win.get_char_creator()
        # get picture of character creator and pack it into the window
        path = self._char_creator.get_image_path()
        image = Gtk.Image.new_from_file(path)
        self._win.pack_in_main_content(image)

        # Get the image from the character creator, and then display it
        self._progress = ProgressBar(self._win.width)
        self._win.pack_in_bottom_bar(self._progress.fixed)

        self._win.show_all()

    def go_to_edit_character_screen(self):
        self.empty_main_content()
        self.empty_bottom_bar()
        CharacterEdit(self._win)


class CharacterEdit(Gtk.EventBox):
    '''Offer the user the option to modify their avatar
    '''

    def __init__(self, win):
        Gtk.EventBox.__init__(self)

        self._win = win

        # Should this be inherited, passed as a variable, or global?
        # Could be a member variable in window.
        self.char_creator = self._win.get_char_creator()
        self._win.pack_in_main_content(self.char_creator)

        save_changes_button = KanoButton("SAVE CHANGES")
        save_changes_button.connect("clicked", self.save_changes)

        discard_changes_button = OrangeButton("DISCARD")
        discard_changes_button.connect("clicked", self.save_changes)
        empty_label = Gtk.Label("")

        button_box = Gtk.ButtonBox()
        button_box.pack_start(discard_changes_button, False, False, 0)
        button_box.pack_start(save_changes_button, False, False, 0)
        button_box.pack_start(empty_label, False, False, 0)

        self._win.pack_in_bottom_bar(button_box)

        self._win.show_all()

    def save_changes(self, widget):
        self.char_creator.save()

    def discard_changes(self):
        '''Don't save, just go back to the edit character screen
        '''
        self.empty_main_content()
        self.empty_bottom_bar()
        CharacterDisplay(self._win)
