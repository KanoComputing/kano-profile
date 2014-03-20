#!/usr/bin/env python

# images.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os


def check_image(name, pre):
    icon_dir = '/usr/share/kano-profile/media/icons'
    filename = '{}_{}.png'.format(pre, name)
    fullpath = os.path.join(icon_dir, filename)
    if os.path.exists(fullpath):
        print '{} exists'.format(fullpath)
    else:
        from randomavatar.randomavatar import Avatar
        avatar = Avatar(rows=10, columns=10)
        image_byte_array = avatar.get_image(
            string=filename,
            width=200, height=200, pad=10)
        avatar.save(
            image_byte_array=image_byte_array,
            save_location=fullpath)
        print '{} created'.format(fullpath)
