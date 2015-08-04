#!/usr/bin/env python

# ProgressDot.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The GUI to show the frontend of the Quests.

from gi.repository import Gtk


class ProgressDot(Gtk.EventBox):
    '''
    A filled or unfilled spot.
    '''

    def __init__(self, filled=False):
        Gtk.EventBox.__init__(self)

        self.get_style_context().add_class("progress_outer_ring")
        self.set_size_request(30, 30)

        align1 = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.5)
        self.add(align1)

        white_ring = Gtk.EventBox()
        white_ring.get_style_context().add_class("progress_white_section")
        white_ring.set_size_request(20, 20)

        align1.add(white_ring)

        align2 = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.5)
        white_ring.add(align2)

        centre = Gtk.EventBox()
        centre.set_size_request(10, 10)
        align2.add(centre)

        if filled:
            # Fill the centre with green
            centre.get_style_context().add_class("progress_centre_filled")
        else:
            # Fill the centre with white
            centre.get_style_context().add_class("progress_centre_unfilled")
