#!/usr/bin/env python

# images.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.utils import ensure_dir
from .paths import image_dir


def get_image(category, subcategory, name, width):
    folder = os.path.join(image_dir, category, width, subcategory)
    filename = '{name}.png'.format(name=name)
    fullpath = os.path.join(folder, filename)
    if not os.path.exists(fullpath):
        try:
            from randomavatar.randomavatar import Avatar
            ensure_dir(folder)
            avatar = Avatar(rows=10, columns=10)
            image_byte_array = avatar.get_image(string=filename, width=width, height=width, pad=10)
            avatar.save(image_byte_array=image_byte_array, save_location=fullpath)
            print '{} created'.format(fullpath)
        except Exception:
            return os.path.join(image_dir, 'icons/50/_missing.png')
    return fullpath


