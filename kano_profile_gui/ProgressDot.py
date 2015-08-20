#!/usr/bin/env python

# ProgressDot.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The GUI to show the frontend of the Quests.

import os
from gi.repository import Gtk, GdkPixbuf
from kano_profile_gui.paths import image_dir


class ProgressDot(Gtk.Fixed):
    '''
    A filled or unfilled spot.
    '''

    def __init__(self, filled=False, color="orange"):
        '''
        Args:
            color (str): "orange", "green" or "grey"
        '''

        Gtk.Fixed.__init__(self)
        self.set_size_request(60, 60)

        white_ring = Gtk.EventBox()
        white_ring.get_style_context().add_class("progress_outer_ring")
        white_ring.set_size_request(44, 44)
        self.put(white_ring, 0, 10)

        align1 = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.5)
        white_ring.add(align1)

        brown_ring = Gtk.EventBox()
        brown_ring.get_style_context().add_class("progress_scroll_section")
        brown_ring.set_size_request(34, 34)

        align1.add(brown_ring)

        align2 = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.5)
        brown_ring.add(align2)

        tick_background = Gtk.EventBox()
        tick_background.get_style_context().add_class("transparent")
        self.put(tick_background, 5, 0)

        if filled:
            self._tick = Tick(50, 50)
            tick_background.add(self._tick)

    @property
    def tick(self):
        return self._tick


class Tick(Gtk.Image):
    def __init__(self, width, height, color="orange", bold=True):
        Gtk.Image.__init__(self)

        if bold:
            tick_file = os.path.join(
                image_dir, "quests/{}-tick.svg".format(color)
            )
        else:
            tick_file = os.path.join(
                image_dir, "quests/{}-tick-stylised.svg".format(color)
            )
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            tick_file, width, height
        )
        self.set_from_pixbuf(pixbuf)
