#!/usr/bin/env python

# progress_bar.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This displays orange progress bar along top of each screen

from gi.repository import Gtk


class Bar():
    def __init__(self, input, WINDOW_WIDTH):
        # Height of the thin part of the progress bar
        self.height = 10
        # Height of the label
        self.label_height = 30
        self.label_width = 60

        # Calculate various widths of bars
        progress_width = (WINDOW_WIDTH - self.label_width) * input
        rest_of_bar_width = (WINDOW_WIDTH - self.label_width) * (1 - input)

        self.progress = Gtk.EventBox()
        self.progress.set_size_request(progress_width, self.height)
        self.progress.get_style_context().add_class("progress_bar")

        self.rest_of_bar = Gtk.EventBox()
        self.rest_of_bar.set_size_request(rest_of_bar_width, self.height)
        self.rest_of_bar.get_style_context().add_class("rest_of_bar")

        self.label = Gtk.Label(str(int(input * 100)) + "%")
        self.label.set_size_request(self.label_width, self.label_height)
        self.label.set_alignment(xalign=0.5, yalign=0.5)
        self.label.get_style_context().add_class("white")

        self.label_background = Gtk.EventBox()
        self.label_background.get_style_context().add_class("progress_label")
        self.label_background.set_size_request(self.label_width, self.label_height)
        self.label_background.add(self.label)

        self.fixed = Gtk.Fixed()
        self.fixed.set_size_request(WINDOW_WIDTH, self.label_height)

        # This background is so we can pretend to overlap with the top bar.
        #self.background = Gtk.EventBox()
        #self.background.set_size_request(WINDOW_WIDTH, self.BAR_HEIGHT)
        #self.background.get_style_context().add_class("black")

        #self.fixed.put(self.background, 0, 0)
        self.fixed.put(self.label_background, progress_width, 0)
        self.fixed.put(self.progress, 0, self.height + 0)
        self.fixed.put(self.rest_of_bar, progress_width + self.label_width, self.height + 0)
