#!/usr/bin/env python

# home_stats.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Display stats to user on home screen

from gi.repository import Gtk
from kano.profile.badges import count_completed_challenges, count_number_of_blocks, count_number_of_shares


class HomeStats():
    def __init__(self, WINDOW_WIDTH):

        # Contains the info about the level and the image
        self.height = 88
        self.container = Gtk.Grid()
        self.container.set_size_request(WINDOW_WIDTH, self.height)

        # Placeholder info
        #completed_challenges = 19

        self.completed_challenges = count_completed_challenges()
        self.blocks_used = count_number_of_blocks()
        self.shares = count_number_of_shares()

        # Stats
        stat_dict = {"Blocks used": self.blocks_used, "Completed challenges": self.completed_challenges, "Shares": self.shares}
        number_of_items = 3

        index = 0

        for title, stat in stat_dict.iteritems():

            box = Gtk.EventBox()
            box.get_style_context().add_class("white")
            box.set_size_request(WINDOW_WIDTH / number_of_items, self.height)
            box_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

            stat_label = Gtk.Label(stat)
            stat_label.get_style_context().add_class("stat_number")
            stat_label.set_alignment(xalign=0.5, yalign=1)
            stat_label.set_size_request(WINDOW_WIDTH / number_of_items, self.height / 2)

            stat_title = Gtk.Label(title)
            stat_title.get_style_context().add_class("stat_title")
            stat_title.set_alignment(xalign=0.5, yalign=0)
            stat_title.set_size_request(WINDOW_WIDTH / number_of_items, self.height / 2)

            box_container.pack_start(stat_label, False, False, 0)
            box_container.pack_start(stat_title, False, False, 0)
            box.add(box_container)

            self.container.attach(box, index, 0, 1, 1)
            index = index + 1
