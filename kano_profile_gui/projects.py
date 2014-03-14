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

    projects_list = []
    for app in apps:
        if app_dirs[app] == 'kanoprofile':
            app_dir = kp.get_app_data_dir(app)
        else:
            app_dir = os.path.expanduser(app_dirs[app])

        files = os.listdir(app_dir)
        files_filtered = [f for f in files if os.path.splitext(f)[1][1:] == app_ext[app]]

        for filename in files_filtered:
            project = dict()
            project['app'] = app
            project['dir'] = app_dir
            project['file'] = filename
            project['display_name'] = os.path.splitext(filename)[0]
            projects_list.append(project)

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
        btn.connect('clicked', load, project['app'], project['file'])
        table.attach(btn, 2, 3, i, i + 1)

        btn = Gtk.Button(label='Share', halign=Gtk.Align.CENTER)
        btn.connect('clicked', share, project['app'], project['file'])
        table.attach(btn, 3, 4, i, i + 1)

        print project


def load(_button, app, file):
    print 'load', app, file
    pass


def share(_button, app, file):
    print 'share', app, file
    pass
