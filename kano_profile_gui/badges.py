#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

#import os
#from gi.repository import Gtk

import os
#from kano.profile.badges import calculate_badges
#from .images import get_image
#from .paths import icon_dir
import kano_profile_gui.components.constants as constants
import kano_profile_gui.selection_table_components.table_template as table_template

img_width = 50
badge_ui = None


def activate(_win, _box):
    global badge_ui

    """_label.set_text('Badges')

                badges = {k: v for k, v in calculate_badges().iteritems() if not k.startswith('swag_')}
                if not badges:
                    return

                num_categories = len(badges.keys())
                max_items = max([len(v) for k, v in badges.iteritems()])

                table = Gtk.Table(num_categories, max_items, False)
                _box.add(table)

                for i, (group, items) in enumerate(badges.iteritems()):
                    for j, (item, unlocked) in enumerate(items.iteritems()):
                        print i, j, group, item, unlocked

                        img = Gtk.Image()
                        if unlocked:
                            img_path = get_image(item, group, img_width)
                            img.set_from_file(img_path)
                        else:
                            img.set_from_file(os.path.join(icon_dir, str(img_width), '_locked.png'))

                        table.attach(img, j, j + 1, i, i + 1)"""

    filenames = []

    for root, dirs, files in os.walk(constants.media + "/badges/"):
        for file in files:
            if file.endswith(".png"):
                filenames.append(os.path.join(root, file))

    badges_info = []

    for i in filenames:
        line = {"filename": i, "heading": "heading", "description": "lots of info"}
        badges_info.append(line)

    headers = ["badges"]
    info = [badges_info]
    equipable = False
    width = 734
    height = 540

    if badge_ui is None:
        badge_ui = table_template.Template(headers, info, equipable, width, height)

    _box.pack_start(badge_ui.container, False, False, 0)

    _win.show_all()

    badge_ui.hide_labels()
