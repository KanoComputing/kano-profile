#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

# setting up directories
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# media dir
media_local = os.path.join(dir_path, 'media')
media_usr = '/usr/share/kano-profile/media/'

if os.path.exists(media_local):
    media_dir = media_local
elif os.path.exists(media_usr):
    media_dir = media_usr
else:
    raise Exception('Neither local nor usr media dir found!')

image_dir = os.path.join(media_dir, 'images')
icon_dir = os.path.join(media_dir, 'images/icons')
css_dir = os.path.join(media_dir, 'CSS')
badges_dir = os.path.join(media_dir, 'images/badges')
avatars_dir = os.path.join(media_dir, 'images/avatars')
environment_dir = os.path.join(media_dir, 'images/environments')
