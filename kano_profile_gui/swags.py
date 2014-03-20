#!/usr/bin/env python

# swags.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import math
from gi.repository import Gtk

import kano.profile as kp
import kano_profile_gui.images as images


def activate(_win, _box, _label):
    _label.set_text('swags')

    swags = kp.calculate_badges_swags('swags')
    if not swags:
        return

    total_number = len(swags)
    dim = int(math.ceil(math.sqrt(total_number)))

    if not dim:
        return

    table = Gtk.Table(dim, dim, False)
    _box.add(table)

    for i, swag in enumerate(swags):
        x = i % dim
        y = i / dim

        # TODO remove avatar generation in production!
        img_path = images.check_image(swag, 'swag')
        img = Gtk.Image()

        if swags[swag]:
            img.set_from_file(img_path)
        else:
            img.set_from_file('/usr/share/kano-profile/media/icons/questionmark.png')

        table.attach(img, x, x + 1, y, y + 1)
