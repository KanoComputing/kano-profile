#!/usr/bin/env python

# badge_screen.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango
from kano_profile_gui.BadgeItem import BadgeItem
from kano_profile_gui.backend import create_item_page_list
from kano_profile_gui.paths import media_dir
from kano_profile_gui.navigation_buttons import create_navigation_button
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano_profile_gui.image_helper_functions import (
    create_translucent_layer, get_image_path_at_size
)


class BadgeScreen(Gtk.EventBox):

    def __init__(self, win):
        Gtk.EventBox.__init__(self)

        self._win = win
        self._page = 0

        css_file = os.path.join(media_dir, "CSS/badge_screen.css")
        apply_styling_to_screen(css_file)

        self.badge_grid = BadgeGrid(win)
        bottom_bar = self._create_bottom_navigation_bar()

        self._win.pack_in_main_content(self.badge_grid)
        self._win.pack_in_bottom_bar(bottom_bar)
        self._load_page()

        self._win.show_all()

    def _create_bottom_navigation_bar(self):
        bottom_bar = Gtk.Box()

        self.next_button = create_navigation_button(_("Next page").upper(),
                                                    "next")
        self.next_button.connect("clicked", self._load_page_wrapper, 1)

        self.prev_button = create_navigation_button(_("Previous").upper(),
                                                    "previous")
        self.prev_button.connect("clicked", self._load_page_wrapper, -1)

        bottom_bar.pack_start(self.prev_button, False, False, 0)
        bottom_bar.pack_end(self.next_button, False, False, 0)
        return bottom_bar

    def _load_page_wrapper(self, widget, page_increment):
        self._page += page_increment
        self._load_page()

    def _load_page(self):
        self.badge_grid.load_page(self._page)
        self._enable_next_prev_button()
        self._win.show_all()

    def _enable_next_prev_button(self):
        max_page_number = self.badge_grid.get_number_of_pages()

        if self._page == 0:
            self.prev_button.set_sensitive(False)
            self.next_button.set_sensitive(True)
        elif self._page == max_page_number - 1:
            self.prev_button.set_sensitive(True)
            self.next_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)
            self.next_button.set_sensitive(True)

    def _create_badge_button(self, name, path):
        button = Gtk.Button()
        image = Gtk.Image.new_from_file(path)

        # It's probably a lot more complicated than this as we need to
        # style the buttons and have a hover over label
        button.add(image)


class BadgeGrid(Gtk.Grid):
    def __init__(self, win):
        Gtk.Grid.__init__(self)
        self._win = win
        self.get_style_context().add_class("badge_grid")
        self.row = 2
        self.column = 3
        self.number_on_page = self.row * self.column

        self._split_info_into_pages()

    def get_number_of_pages(self):
        return len(self.page_list)

    def _split_info_into_pages(self):
        self.badge_list, self.page_list = create_item_page_list(
            self.row, self.column
        )

    def _pack_badge_grid(self, page_number):
        badge_list = self.page_list[page_number]

        for i in range(len(badge_list)):
            badge_info = badge_list[i]

            row = badge_info['row']
            column = badge_info['column']
            badge_widget = BadgeItem(badge_info)

            # This is the index of the badge in the ordered array of all the
            # badges
            index = page_number * self.number_on_page + i
            badge_widget.connect("clicked", self._go_to_badge_info_wrapper,
                                 index)
            self.attach(badge_widget, column, row, 1, 1)

    def _go_to_badge_info_wrapper(self, widget, index):
        self._go_to_badge_info(index)

    def _go_to_badge_info(self, index):
        self._win.empty_main_content()
        self._win.empty_bottom_bar()
        BadgeInfoScreen(self._win, self.badge_list, index)

    def _unpack_badge_grid(self):
        for child in self.get_children():
            self.remove(child)

    def load_page(self, page):
        self._unpack_badge_grid()
        self._pack_badge_grid(page)


class BadgeInfoScreen(Gtk.EventBox):
    '''This screen shows the large version of the badge image,
    the title and the description
    '''

    def __init__(self, win, item_list, index):
        '''
        item_info is the dictionary of the selected item
        item_list is the ordered list of badges
        '''

        self._win = win
        self.image_width = 460
        self.image_height = 448

        # these are the data structures
        self.item_list = item_list
        self.index = index

        self.item_info = self.item_list[index]

        self._show_badge()
        # set the background of the badge part to the colour
        # described by the item_info
        self._create_bottom_navigation_bar()
        self._win.show_all()

    def _show_badge(self):
        background = Gtk.EventBox()

        # TODO: this is repeated.  Fix this.
        locked = not self.item_info['achieved']
        if locked:
            color = Gdk.RGBA()
            color.parse('#dddddd')
        else:
            bg_color = self.item_info['bg_color']
            color = Gdk.RGBA()
            color.parse('#' + bg_color)

        background.override_background_color(Gtk.StateFlags.NORMAL,
                                             color)

        badge_fixed = self.create_badge_fixed(self.item_info)

        info_box = self._create_info_box()

        hbox = Gtk.Box()
        hbox.pack_start(badge_fixed, False, False, 0)
        hbox.pack_start(info_box, False, False, 0)

        background.add(hbox)
        self._win.pack_in_main_content(background)

    def _create_info_box(self):
        info_width = 200

        info_box = Gtk.EventBox()
        info_box.set_size_request(info_width, -1)
        info_box.get_style_context().add_class("info_box")
        info_box.set_margin_top(20)
        info_box.set_margin_bottom(100)
        info_box.set_margin_right(20)

        title = self.item_info["title"]
        locked = not self.item_info['achieved']

        if locked:
            description = self.item_info["desc_locked"]
        else:
            description = self.item_info["desc_unlocked"]

        title_label = Gtk.Label(title, xalign=0)
        title_label.get_style_context().add_class("info_heading")

        description_label = Gtk.Label(description, xalign=0)
        description_label.get_style_context().add_class("info_paragraph")
        description_label.set_line_wrap(True)
        description_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        description_label.set_size_request(info_width, -1)
        # TODO: Figure out a way of doing the line wrap according to size
        # instead of relying on characters
        description_label.set_max_width_chars(20)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(title_label, False, False, 0)
        vbox.pack_start(description_label, False, False, 0)

        info_box.add(vbox)

        return info_box

    # TODO: move this outside, or get this from inheritance,
    # as this is the same height across all screens
    def _create_bottom_navigation_bar(self):
        bottom_bar = Gtk.ButtonBox()

        self.prev_button = create_navigation_button(_("Previous").upper(),
                                                    "previous")
        self.prev_button.connect("clicked", self._go_to_other_badge, -1)

        self.grid_button = create_navigation_button(_("Back to grid").upper(),
                                                    "middle")
        self.grid_button.connect("clicked", self._go_to_grid)

        self.next_button = create_navigation_button(_("Next").upper(), "next")
        self.next_button.connect("clicked", self._go_to_other_badge, 1)

        bottom_bar.pack_start(self.prev_button, False, False, 0)
        bottom_bar.pack_start(self.grid_button, False, False, 0)
        bottom_bar.pack_end(self.next_button, False, False, 0)
        # TODO: move this to CSS
        bottom_bar.set_margin_top(25)

        self._win.pack_in_bottom_bar(bottom_bar)

    def _make_index_in_range(self, index):
        '''Making sure the index is valid by returning one that is.
        Returns a number between 0 and the number of items in the grid.
        '''
        total_num_of_items = len(self.item_list)
        new_index = index % total_num_of_items
        return new_index

    def _go_to_other_badge(self, widget, change_index):
        # we know the index of the current widget, so we
        # need to change the index, get the new selected,
        # unpack the current widgets and pack the new widgets
        self._win.empty_bottom_bar()
        self._win.empty_main_content()
        new_index = self._make_index_in_range(self.index + change_index)
        BadgeInfoScreen(self._win, self.item_list, new_index)

    def _go_to_grid(self, widget):
        self._win.empty_bottom_bar()
        self._win.empty_main_content()
        BadgeScreen(self._win)

    def _get_item_colour(self):
        return self.item_info['bg_color']

    def create_badge_fixed(self, badge_info):
        '''
        Get the file path for the badge, pack it and optionally add
        an overlay.
        '''

        locked = not badge_info['achieved']
        force_locked = False

        fixed = Gtk.Fixed()
        img = Gtk.Image()
        fixed.set_size_request(self.image_width, self.image_height)

        # New system
        if 'image' in badge_info:
            path = badge_info['image']

            if locked:
                force_locked = True

            width = 330
            height = 330
            fixed.put(img, 60, 60)

        # Old system
        else:
            category = badge_info['category']
            name = badge_info['name']
            width = self.image_width
            height = self.image_height
            path = get_image_path_at_size(
                category, name, width, height, locked
            )
            fixed.put(img, 0, 0)

        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(path, width, height)
        img.set_from_pixbuf(pb)

        if force_locked:
            translucent_layer = create_translucent_layer(
                self.image_width, self.image_height
            )
            fixed.put(translucent_layer, 0, 0)

        return fixed
