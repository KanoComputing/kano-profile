#!/usr/bin/env python

# character_screens.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
import os
from gi.repository import Gtk, GdkPixbuf
from kano_profile_gui.progress_bar import ProgressBar
from kano.gtk3.buttons import KanoButton, OrangeButton
from kano_profile_gui.paths import media_dir
from kano.logging import logger

from kano_profile.apps import load_app_state_variable


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

        icon_filename = os.path.join(media_dir, "images/icons/edit.png")
        self.cog_widget_icon = Gtk.Image.new_from_file(icon_filename)

        launch_char_creator_btn = Gtk.Button()
        hbox = Gtk.Box()
        edit_label = Gtk.Label(_("Edit").upper())
        edit_label.set_margin_right(7)

        hbox.pack_start(self.cog_widget_icon, False, False, 0)
        hbox.pack_end(edit_label, False, False, 0)

        launch_char_creator_btn.connect("clicked", self.go_to_edit_character_screen)
        launch_char_creator_btn.connect("enter-notify-event", self.set_orange_cog)
        launch_char_creator_btn.connect("leave-notify-event", self.set_grey_cog)
        launch_char_creator_btn.get_style_context().add_class("character_cog")
        launch_char_creator_btn.add(hbox)

        # Pack this part of the screen into the window
        self._char_creator = self._win.char_creator

        # Get picture of character creator and pack it into the window
        path = self._char_creator.get_image_path()

        if not os.path.exists(path):
            # Usually we wouldn't be in this state, but just in case
            from kano_profile.profile import recreate_char, block_and_sync
            logger.warn('Character assets not there, will sync and recreate')
            block_and_sync()
            recreate_char(block=True)

        image = Gtk.Image.new_from_file(path)

        self.fixed = Gtk.Fixed()
        self.fixed.put(image, 0, 0)
        self.fixed.put(launch_char_creator_btn, 30, 30)
        self.put_pet_on_char_creator()

        self._win.pack_in_main_content(self.fixed)
        self._pack_progress_bar()

        self._win.show_all()

    def put_pet_on_char_creator(self):
        # Check for pet. If pet has been hatched, then show on the character
        # creator
        egg_hatched = (load_app_state_variable("kano-egg", "level") == "2")
        if egg_hatched:
            hatched_path = os.path.join(
                os.path.expanduser("~"),
                "content/hatched.png"
            )
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(hatched_path, -1, 200)
            pet_image = Gtk.Image.new_from_pixbuf(pixbuf)
            self.fixed.put(pet_image, 390, 200)

    def set_orange_cog(self, widget, event):
        icon_filename = os.path.join(media_dir, "images/icons/edit-active.png")
        self.cog_widget_icon.set_from_file(icon_filename)

    def set_grey_cog(self, widget, event):
        icon_filename = os.path.join(media_dir, "images/icons/edit.png")
        self.cog_widget_icon.set_from_file(icon_filename)

    def _pack_progress_bar(self):

        # Get the image from the character creator, and then display it
        self._progress = ProgressBar(self._win.width)
        alignment = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        alignment.add(self._progress)
        self._win.pack_in_bottom_bar(alignment)

    def go_to_edit_character_screen(self, widget=None):
        self._win.empty_main_content()
        self._win.empty_bottom_bar()
        CharacterEdit(self._win, self._char_creator)


class CharacterEdit(Gtk.EventBox):
    '''Offer the user the option to modify their avatar
    '''

    def __init__(self, win, char_creator):
        Gtk.EventBox.__init__(self)

        self._win = win

        # Should this be inherited, passed as a variable, or global?
        # Could be a member variable in window.
        # self.char_creator = self._win.get_char_creator()
        self.char_creator = char_creator
        self._win.pack_in_main_content(self.char_creator)
        self.char_creator.reset_selected_menu_items()

        save_changes_button = KanoButton(_("Save changes").upper())
        save_changes_button.connect("clicked", self.save_changes)

        discard_changes_button = OrangeButton(_("Discard").upper())
        discard_changes_button.connect("clicked", self.discard)
        discard_changes_button.set_margin_left(100)
        empty_label = Gtk.Label("")

        button_box = Gtk.ButtonBox()
        button_box.pack_start(discard_changes_button, False, False, 0)
        button_box.pack_start(save_changes_button, False, False, 0)
        button_box.pack_start(empty_label, False, False, 0)

        self._win.pack_in_bottom_bar(button_box)
        self._win.show_all()

        # Hide all the pop ups
        self.char_creator._hide_pop_ups()

    def save_changes(self, widget):
        self.char_creator.save()
        self._go_back_to_display_screen()

    def discard(self, widget):
        self.char_creator.update_from_saved_image()
        self._go_back_to_display_screen()

    def _go_back_to_display_screen(self):
        '''Don't save, just go back to the edit character screen
        '''
        self._win.empty_main_content()
        self._win.empty_bottom_bar()
        CharacterDisplay(self._win)
