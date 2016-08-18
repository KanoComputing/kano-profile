#!/usr/bin/env python

# progress_bar.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This displays orange progress bar along top of each screen

import os
from gi.repository import Gtk
from kano_profile.badges import calculate_min_current_max_xp
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano_profile_gui.paths import media_dir


class ProgressBar(Gtk.Fixed):

    def __init__(self, window_width):

        Gtk.Fixed.__init__(self)

        css_path = os.path.join(media_dir, "CSS/progress_bar.css")
        apply_styling_to_screen(css_path)

        # Height of the thin part of the progress bar
        self.height = 10

        # Height of the label
        self.label_height = 30
        self.label_width = 50

        # Allow for margin on either side of the progress bar
        self.total_width = window_width - 60

        self.progress = Gtk.EventBox()
        self.progress.get_style_context().add_class('progress_bar')

        self.rest_of_bar = Gtk.EventBox()
        self.rest_of_bar.get_style_context().add_class('rest_of_bar')

        self.progress_label = Gtk.Label()
        self.progress_label.set_alignment(xalign=0.5, yalign=0.5)

        self.endpoint_label = Gtk.Label()
        self.endpoint_label.set_alignment(xalign=0.5, yalign=0.5)

        self.label_background = Gtk.EventBox()
        self.label_background.get_style_context().add_class('progress_background')
        self.label_background.set_size_request(self.label_width, self.label_height)
        self.label_background.add(self.progress_label)

        self.endpoint_background = Gtk.EventBox()
        self.endpoint_background.get_style_context().add_class('endpoint_background')
        self.endpoint_background.set_size_request(self.label_width, self.label_height)
        self.endpoint_background.add(self.endpoint_label)

        self.set_size_request(self.total_width, self.label_height)

        self.set_progress()

    def set_progress(self):

        # Calculate xp_start, xp_progress, xp_end here
        xp_start, xp_progress, xp_end = calculate_min_current_max_xp()

        self.fraction = (xp_progress - xp_start + 0.0) / (xp_end - xp_start)
        progress_width = (self.total_width - self.label_width) * self.fraction
        rest_of_bar_width = (self.total_width - self.label_width) * (1 - self.fraction)

        self.progress.set_size_request(progress_width, self.height)
        self.rest_of_bar.set_size_request(rest_of_bar_width, self.height)

        for child in self.get_children():
            self.remove(child)

        self.progress_label.set_text(str(xp_progress))
        self.endpoint_label.set_text(str(xp_end))

        self.put(self.progress, 0, self.height)
        self.put(self.rest_of_bar, progress_width + self.label_width, self.height)
        self.put(self.endpoint_background, self.total_width - self.label_width, 0)
        self.put(self.label_background, progress_width, 0)

    def get_progress(self):
        return self.fraction
