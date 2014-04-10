#!/usr/bin/env python

# projects.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk

from kano.profile.apps import get_app_list, get_app_data_dir
from kano.utils import run_print_output_error

app_profiles = {
    'make-pong': {
        'dir': '~/Pong-content',
        'ext': 'xml',
        'cmd': 'python /usr/share/make-pong/make-pong {fullpath}'

    },
    'make-snake': {
        'dir': 'kanoprofile',
        'ext': '',
        'cmd': 'kano-launcher "rxvt -title \'Make Snake\' -e python /usr/share/make-snake -t custom" "make-snake"'
    }
}


def activate(_win, _box, _label):
    _label.set_text('Projects')

    apps = get_app_list(include_empty=False)

    projects_list = []
    for app in apps:
        if app_profiles[app]['dir'] == 'kanoprofile':
            data_dir = get_app_data_dir(app)
        else:
            data_dir = os.path.expanduser(app_profiles[app]['dir'])

        files = os.listdir(data_dir)
        files_filtered = [f for f in files if os.path.splitext(f)[1][1:] == app_profiles[app]['ext']]

        for filename in files_filtered:
            project = dict()
            project['app'] = app
            project['data_dir'] = data_dir
            project['file'] = filename
            project['display_name'] = os.path.splitext(filename)[0]
            projects_list.append(project)

    if not projects_list:
        return

    table = Gtk.Table(4, len(projects_list), True)
    _box.add(table)

    for i, project in enumerate(projects_list):
        label = Gtk.Label()
        label.set_text(project['app'])
        table.attach(label, 0, 1, i, i + 1)

        label = Gtk.Label()
        label.set_text(project['display_name'])
        table.attach(label, 1, 2, i, i + 1)

        btn = Gtk.Button(label='Load', halign=Gtk.Align.CENTER)
        btn.connect('clicked', load, project['app'], project['file'], project['data_dir'])
        table.attach(btn, 2, 3, i, i + 1)

        btn = Gtk.Button(label='Share', halign=Gtk.Align.CENTER)
        btn.connect('clicked', share, project['app'], project['file'])
        table.attach(btn, 3, 4, i, i + 1)


def load(_button, app, filename, data_dir):
    print 'load', app, filename, data_dir
    fullpath = os.path.join(data_dir, filename)
    cmd = app_profiles[app]['cmd'].format(fullpath=fullpath, filename=filename)
    run_print_output_error(cmd)


def share(_button, app, filename):
    print 'share', app, filename
