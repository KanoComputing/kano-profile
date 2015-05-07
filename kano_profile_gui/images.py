#!/usr/bin/env python

# images.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.logging import logger
from .paths import image_dir
from kano_profile.paths import online_badges_dir


# "Badge", folder_name, file_name, width of image
def get_image(category, subcategory, name, subfolder_str):
    # The online badge image files are stored in the home directory.
    # The function bellow gets the corrects path.
    if category == "badges" and subcategory == "online":
        return get_online_badge_path(name)

    folder = os.path.join(image_dir, category, subfolder_str, subcategory)
    filename = '{name}.png'.format(name=name)
    fullpath = os.path.join(folder, filename)
    if not os.path.exists(fullpath):
        logger.error('missing image: {}'.format(fullpath))
        return os.path.join(image_dir, 'icons/50/_missing.png')
        #ensure_dir(folder)
        #open(fullpath, 'w').close()
        #print '{} created'.format(fullpath)
        # try:
        #     from randomavatar.randomavatar import Avatar
        #     ensure_dir(folder)
        #     avatar = Avatar(rows=10, columns=10)
        #     image_byte_array = avatar.get_image(string=filename, width=width, height=width, pad=10)
        #     avatar.save(image_byte_array=image_byte_array, save_location=fullpath)
        #     print '{} created'.format(fullpath)
        # except Exception:
        #     return os.path.join(image_dir, 'icons/50/_missing.png')
    return fullpath


def get_online_badge_path(name):
    return os.path.join(online_badges_dir, "{}.png".format(name))
