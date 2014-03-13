#!/usr/bin/env python

# projects.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk

import kano.profile as kp


def activate(_win, _box, _label):
    _label.set_text('Projects')

    apps = kp.get_app_list(include_empty=False)

    app_dirs = {
        'make-pong': '~/Pong-content',
        'make-snake': 'kanoprofile'
    }

    app_ext = {
        'make-pong': 'xml',
        'make-snake': ''
    }

    msg = ''

    for app in apps:
        if app_dirs[app] == 'kanoprofile':
            app_dir = kp.get_app_data_dir(app)
        else:
            app_dir = os.path.expanduser(app_dirs[app])

        files = os.listdir(app_dir)
        files_filtered = [f for f in files if os.path.splitext(f)[1][1:] == app_ext[app]]

        msg += 'app: {}\n'.format(app)
        msg += 'dir: {}\n'.format(app_dir)
        msg += 'files: {}\n\n'.format(', '.join(files_filtered))

    label = Gtk.Label()
    label.set_text(msg)
    _box.add(label)



