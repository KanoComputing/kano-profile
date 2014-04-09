#!/usr/bin/env python

# images.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

# setting up directories
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
media_local = os.path.join(dir_path, 'media')
media_usr = '/usr/share/kano-profile/media/'

if os.path.exists(media_local):
    media_dir = media_local
elif os.path.exists(media_usr):
    media_dir = media_usr
else:
    raise Exception('Neither local nor usr rules found!')


def get_image(name, category, width):
    icon_dir = os.path.join(media_dir, 'icons')
    filename = '{width}/{category}_{name}.png'.format(width=width, category=category, name=name)
    fullpath = os.path.join(icon_dir, filename)
    if not os.path.exists(fullpath):
        try:
            from randomavatar.randomavatar import Avatar
            avatar = Avatar(rows=10, columns=10)
            image_byte_array = avatar.get_image(string=filename, width=width, height=width, pad=10)
            avatar.save(image_byte_array=image_byte_array, save_location=fullpath)
            print '{} created'.format(fullpath)
        except Exception:
            return os.path.join(icon_dir, '_missing.png')
    return fullpath
