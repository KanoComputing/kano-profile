#!/usr/bin/env python

# images.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os


def get_image(name, pre):
    icon_dir = '/usr/share/kano-profile/media/icons'
    filename = '{}_{}.png'.format(pre, name)
    fullpath = os.path.join(icon_dir, filename)
    if not os.path.exists(fullpath):
        # TODO: remove random avatar generation from production!
        from randomavatar.randomavatar import Avatar
        avatar = Avatar(rows=10, columns=10)
        image_byte_array = avatar.get_image(
            string=filename,
            width=108, height=108, pad=10)
        avatar.save(
            image_byte_array=image_byte_array,
            save_location=fullpath)
        print '{} created'.format(fullpath)
    return fullpath
