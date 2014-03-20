#!/usr/bin/env python

# dialogs.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import sys
from gi.repository import Gtk

import kano_profile_gui.images as images


class MainWindow(Gtk.Window):
    def __init__(self, levelUp, newBadges, newSwags):
        if levelUp:
            title = 'Level Up!'
        elif newBadges:
            title = 'New Badges!'
        elif newSwags:
            title = 'New Swags!'
        else:
            sys.exit('Nothing to display!')

        # Create main window
        Gtk.Window.__init__(self, title=title)
        self.set_size_request(300, 200)

        # Create common elements
        # Main table
        table = Gtk.Table(2, 1, False)
        self.add(table)

        if levelUp:
            msg = 'New level: {}!'.format(levelUp)
            label = Gtk.Label()
            label.set_text(msg)
            table.attach(label, 0, 1, 0, 1)

        elif newBadges:
            icon_table = Gtk.Table(len(newBadges), 2, False)
            for i, badge in enumerate(newBadges):
                img_path = images.get_image(badge, 'badge')
                img = Gtk.Image()
                img.set_from_file(img_path)
                icon_table.attach(img, i, i + 1, 0, 1)

                label = Gtk.Label()
                label.set_text(badge)
                icon_table.attach(label, i, i + 1, 1, 2)
            table.attach(icon_table, 0, 1, 0, 1)

        elif newSwags:
            icon_table = Gtk.Table(len(newSwags), 2, False)
            for i, swag in enumerate(newSwags):
                img_path = images.get_image(swag, 'swag')
                img = Gtk.Image()
                img.set_from_file(img_path)
                icon_table.attach(img, i, i + 1, 0, 1)

                label = Gtk.Label()
                label.set_text(swag)
                icon_table.attach(label, i, i + 1, 1, 2)
            table.attach(icon_table, 0, 1, 0, 1)

        # OK Button
        button = Gtk.Button(label='OK', halign=Gtk.Align.CENTER)
        button.connect('clicked', Gtk.main_quit)
        table.attach(button, 0, 1, 1, 2)


def show(levelUp=None, newBadges=None, newSwags=None):
    win = MainWindow(levelUp, newBadges, newSwags)
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
