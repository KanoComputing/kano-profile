#!/usr/bin/env python

# home_stats.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Display stats to user on home screen

from gi.repository import Gtk

BAR_HEIGHT = 100


class Stats():
    def __init__(self, WINDOW_WIDTH, stat_dict):

        #stat_titles = ["Name", "Level", "Progress to next level", "Completion"]

        # Contains the info about the level and the image
        self.container = Gtk.Grid()
        self.container.set_size_request(WINDOW_WIDTH, BAR_HEIGHT)
        index = 0

        for title, stat in stat_dict.iteritems():

            box = Gtk.EventBox()
            box.get_style_context().add_class("white")
            box.set_size_request(WINDOW_WIDTH / 4, BAR_HEIGHT)
            box_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

            stat_label = Gtk.Label(stat)
            stat_label.get_style_context().add_class("stat_number")
            stat_label.set_alignment(xalign=0.5, yalign=1)
            stat_label.set_size_request(WINDOW_WIDTH / 4, BAR_HEIGHT / 2)

            stat_title = Gtk.Label(title)
            stat_title.get_style_context().add_class("stat_title")
            stat_title.set_alignment(xalign=0.5, yalign=0)
            stat_title.set_size_request(WINDOW_WIDTH / 4, BAR_HEIGHT / 2)

            box_container.pack_start(stat_label, False, False, 0)
            box_container.pack_start(stat_title, False, False, 0)
            box.add(box_container)

            self.container.attach(box, index, 0, 1, 1)
            index = index + 1
