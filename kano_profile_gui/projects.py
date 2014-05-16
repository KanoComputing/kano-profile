#!/usr/bin/env python

# projects.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import json
from gi.repository import Gtk
from kano.profile.apps import get_app_list, get_app_data_dir
from kano.utils import run_print_output_error
from kano.profile.paths import rules_dir

app_profiles = None


# The list of the displayed items
class ProjectList():
    def __init__(self):
        global app_profiles

        self.width = 646
        self.height = 88

        apps = get_app_list()

        self.projects_list = []
        app_profiles = {}

        with open(rules_dir + "/app_profiles.json") as json_file:
            app_profiles = json.load(json_file)

        for app in apps:
            if app in app_profiles:
                if 'ext' in app_profiles[app]:
                    if app_profiles[app]['dir'] == 'kanoprofile':
                        data_dir = get_app_data_dir(app)
                    else:
                        data_dir = os.path.expanduser(app_profiles[app]['dir'])

                    icon_path = app_profiles[app]['icon']

                    if not os.path.exists(data_dir):
                        continue

                    files = os.listdir(data_dir)
                    files_filtered = [f for f in files if os.path.splitext(f)[1][1:] == app_profiles[app]['ext']]

                    for filename in files_filtered:
                        project = dict()
                        project['app'] = app
                        project['data_dir'] = data_dir
                        project['file'] = filename
                        project['display_name'] = os.path.splitext(filename)[0]
                        project['icon'] = icon_path
                        self.projects_list.append(project)

        self.background = Gtk.EventBox()
        self.background.get_style_context().add_class("project_list_background")

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.align = Gtk.Alignment(xalign=0.5, yalign=0.5)
        self.align.set_padding(10, 10, 20, 20)
        self.align.add(self.container)
        self.background.add(self.align)

        if not self.projects_list:
            return

        for i, project in enumerate(self.projects_list):
            item = ProjectItem(project)
            self.container.pack_start(item.background, False, False, 0)


# Each item shown in the list
class ProjectItem():
    def __init__(self, project):
        self.background = Gtk.EventBox()
        self.background.get_style_context().add_class("white")

        self.button = Gtk.Button("MAKE")
        self.button.connect("clicked", self.load, project['app'], project['file'], project['data_dir'])
        self.button.get_style_context().add_class("project_make_button")
        self.button_padding = Gtk.Alignment(xscale=1, yscale=1, xalign=0.5, yalign=0.5)
        self.button_padding.set_padding(25, 25, 10, 10)
        self.button_padding.add(self.button)

        self.title = Gtk.Label(project["display_name"])
        self.title.get_style_context().add_class("project_item_title")
        self.title.set_alignment(xalign=0, yalign=1)

        self.label_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.label_container.pack_start(self.title, False, False, 0)

        self.label_align = Gtk.Alignment(xalign=0, yalign=0.5, xscale=1, yscale=0)
        self.label_align.add(self.label_container)
        self.label_align.set_padding(0, 0, 10, 0)

        self.image = Gtk.Image()
        self.image.set_from_file(project["icon"])

        self.container = Gtk.Box()
        self.container.pack_start(self.image, False, False, 0)
        self.container.pack_start(self.label_align, False, False, 0)
        self.container.pack_end(self.button_padding, False, False, 0)

        self.background.add(self.container)

    def load(self, _button, app, filename, data_dir):
        print 'load', app, filename, data_dir
        fullpath = os.path.join(data_dir, filename)
        cmd = app_profiles[app]['cmd'].format(fullpath=fullpath, filename=filename)
        run_print_output_error(cmd)

    def share(self, _button, app, filename):
        print 'share', app, filename


def activate(_win, _box):
    project_list = ProjectList()

    header_box = Gtk.Box()
    header_box.set_size_request(734, 44)
    header_halign = Gtk.Alignment(xscale=0.0, yscale=0.0, xalign=0.5, yalign=0.5)
    header_halign.set_size_request(734, 44)
    header_title_label = Gtk.Label("CHALLENGES")
    header_title_label.get_style_context().add_class("heading")
    header_halign.add(header_title_label)
    header_box.add(header_halign)

    scrolledwindow = Gtk.ScrolledWindow()
    scrolledwindow.add_with_viewport(project_list.background)
    scrolledwindow.set_size_request(734, 404)
    _box.pack_start(header_box, False, False, 0)
    _box.pack_start(scrolledwindow, False, False, 0)
    _win.show_all()
