#!/usr/bin/env python

# PageControl.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This creates a widget that you can use to control the screen

from gi.repository import Gtk, GObject
from kano.gtk3.buttons import OrangeButton
from kano.logging import logger
from kano.gtk3.cursor import attach_cursor_events


class PageControl(Gtk.Alignment):

    __gsignals__ = {
        'back-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, ()),  # (int,)),
        'next-button-clicked': (GObject.SIGNAL_RUN_FIRST, None, ())  # (int,))
    }

    def __init__(self,
                 num_of_pages=3,
                 selected_page=1,
                 back_text="BACK",
                 next_text="NEXT"):

        Gtk.Alignment.__init__(self, xalign=0.5, xscale=0)
        self.num_of_pages = num_of_pages
        self.selected = selected_page

        self._box = Gtk.Box()
        self.add(self._box)

        # The back button has subtly different styling to the next button
        # When the back button is disabled, it goes invisible, while
        # the NEXT button goes grey.
        self._back_button = OrangeButton(back_text)
        self._back_button.connect("clicked", self.back_button_clicked)
        attach_cursor_events(self._back_button)

        self._next_button = OrangeButton(next_text)
        self._next_button.connect("clicked", self.next_button_clicked)
        attach_cursor_events(self._next_button)

        self.dot_box = Gtk.Box()
        self._create_progress_dots(self.selected)
        self._box.pack_start(self._back_button, False, False, 40)
        self._box.pack_start(self.dot_box, False, False, 0)
        self._box.pack_start(self._next_button, False, False, 40)

        if self.selected == 1:
            self._back_button.set_sensitive(False)
        if self.selected == self.num_of_pages:
            self._next_button.set_sensitive(False)

        # self.connect("next-button-clicked", self.select_dot)
        # self.connect("back-button-clicked", self.select_dot)

    @property
    def back_button(self):
        return self._back_button

    @property
    def next_button(self):
        return self._next_button

    def disable_buttons(self):
        self._next_button.set_sensitive(False)
        self._back_button.set_sensitive(False)

    def enable_next(self):
        self._next_button.set_sensitive(True)

    def enable_back(self):
        self._back_button.set_sensitive(True)

    def disable_next(self):
        self._next_button.set_sensitive(False)

    def disable_back(self):
        self._back_button.set_sensitive(False)

    def set_back_button_text(self, text):
        self._back_button.set_label(text)

    def set_next_button_text(self, text):
        self._next_button.set_label(text)

    def get_back_button(self):
        return self._back_button

    def get_next_button(self):
        return self._next_button

    # TODO: these are expanding to fill the parent container.
    def _create_progress_dots(self, index):
        '''Index is a number from1 to 3, and represents which is
        the selected dot (i.e selected page number)
        '''

        logger.debug("Creating dots")

        for child in self.dot_box.get_children():
            self.dot_box.remove(child)

        for i in range(self.num_of_pages):
            if i + 1 == index:
                dot = self.selected_dot()
                dot.set_margin_left(3)
                dot.set_margin_right(3)
                dot.set_margin_top(9)
                dot.set_margin_bottom(9)
            else:
                dot = self.unselected_dot()
                dot.set_margin_left(5)
                dot.set_margin_right(5)
                dot.set_margin_top(11)
                dot.set_margin_bottom(11)

            self.dot_box.pack_start(dot, False, False, 0)

        self.dot_box.show_all()

    def unselected_dot(self):
        '''Produce an unselected grey spot
        '''

        grey_dot = Gtk.EventBox()
        grey_dot.get_style_context().add_class("grey_dot")
        grey_dot.set_size_request(6, 6)
        return grey_dot

    def selected_dot(self):
        '''Produce a selected orange dot
        '''

        orange_dot = Gtk.EventBox()
        orange_dot.get_style_context().add_class("orange_dot")
        orange_dot.set_size_request(10, 10)
        return orange_dot

    # these functions may not be needed
    def select_dot(self, widget, index):
        '''index is the integers 1 - 3, to represent the page numbers
        '''

        if index not in range(self.num_of_pages):
            return

        self._create_progress_dots(index)

        if index == 1:
            self._back_button.set_sensitive(False)
            self._next_button.set_sensitive(True)
        elif index == self.num_of_pages:
            self._next_button.set_sensitive(False)
            self._back_button.set_sensitive(True)
        else:
            self._next_button.set_sensitive(True)
            self._back_button.set_sensitive(True)

        self.show_all()

    # These give external windows a way of knowing when these buttons have been
    # clicked, without mixing up the classes
    def back_button_clicked(self, widget):
        # Are these needed?
        # self.selected -= 1
        self.emit('back-button-clicked')  # , self.selected)

    def next_button_clicked(self, widget):
        # self.selected += 1
        self.emit('next-button-clicked')  # , self.selected)
