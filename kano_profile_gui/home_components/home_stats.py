#!/usr/bin/env python

# home_stats.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Display stats to user on home screen

from gi.repository import Gtk
from kano.profile.apps import load_app_state_variable


class HomeStats():
    def __init__(self, WINDOW_WIDTH):

        # Contains the info about the level and the image
        self.height = 88
        self.container = Gtk.Grid()
        self.container.set_size_request(WINDOW_WIDTH, self.height)

        # Placeholder info
        completed_challenges = 19
        self.get_blocks_used()
        self.get_shares()

        # Stats
        stat_dict = {"Blocks used": self.blocks_used, "Completed challenges": completed_challenges, "Shares": self.shares}
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

    def get_blocks_used(self):
        pong_blocks = load_app_state_variable("make-pong", "blocks_created")
        if pong_blocks is None:
            pong_blocks = 0

        minecraft_blocks = load_app_state_variable("make-minecraft", "blocks_created")
        if minecraft_blocks is None:
            minecraft_blocks = 0

        self.blocks_used = pong_blocks + minecraft_blocks

    def get_shares(self):
        pong_shares = load_app_state_variable("make-pong", "shares")
        if pong_shares is None:
            pong_shares = 0

        minecraft_shares = load_app_state_variable("make-minecraft", "shares")
        if minecraft_shares is None:
            minecraft_shares = 0

        self.shares = pong_shares + minecraft_shares
