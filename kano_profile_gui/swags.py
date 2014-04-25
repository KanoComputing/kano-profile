#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# swags.py
#
# Controls UI of swag screen

#from gi.repository import Gtk

#import os

from kano.profile.badges import calculate_badges
#from .images import get_image
#from .paths import icon_dir
#import kano_profile_gui.components.constants as constants
import kano_profile_gui.selection_table_components.table_template as table_template

img_width = 50
swag_ui = None


def activate(_win, _box):
    global swag_ui
    #_label.set_text('Swags')

    badges = {k: v for k, v in calculate_badges().iteritems() if k.startswith('swag_')}
    if not badges:
        return

    ## Zsolt's code

    """ num_categories = len(badges.keys())
    max_items = max([len(v) for k, v in badges.iteritems()])

    table = Gtk.Table(num_categories, max_items, False)
    _box.add(table)

    for i, (group, items) in enumerate(badges.iteritems()):
        for j, item in enumerate(items):
            print i, j, group, item, items[item]

            img = Gtk.Image()
            if items[item]:
                img_path = get_image(item, group, img_width)
                img.set_from_file(img_path)
            else:
                img.set_from_file(os.path.join(icon_dir, str(img_width), '_locked.png'))

            table.attach(img, j, j + 1, i, i + 1)"""

    ##### My code ####

    """ badges =
        {u'easter_eggs': {u'file_finder': False},
        u'application': {u'staying_super': False, u'feedbacker': False},
        u'number': {u'silver_medallion': False, u'bronze_medallion': False, u'100_blocks': False},
        u'in_game': {u'appetite_for_apples': False, u'pong_painter': False, u'rule_braker': False},
        u'master': {u'computer_commander': True, u'snake_survivor': False, u'kano_apprentice': False, u'video_voyager': False},
        u'online': {u'community_champion': False, u'talent_tracker': False}}"""

    #environments = {u'environments': {u'Kano-environment1': False}}
    #avatars = {u'avatars': {u'Avatar-1': False, u'Avatar-2': False, u'Avatar-3': False, u'Avatar-4': False, u'Avatar-5': False, u'Avatar-6': True}}

    headers = ["environments", "avatars"]
    #info = [environments, avatars]
    equipable = True
    width = 734
    height = 540

    if swag_ui is None:
        swag_ui = table_template.Template(headers, equipable, width, height)

    _box.pack_start(swag_ui.container, False, False, 0)

    _win.show_all()

    # Hide all labels on images
    swag_ui.hide_labels()
