#!/usr/bin/env python

# projects.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# -*- coding: utf-8 -*-

import os
from gi.repository import Gtk
from kano.utils import get_home, read_json
from kano_profile.apps import get_app_list, get_app_data_dir, launch_project
from kano_profile.paths import app_profiles_file
from kano.logging import logger
import kano.gtk3.cursor as cursor
from kano.gtk3.scrolled_window import ScrolledWindow
import kano_profile_gui.components.icons as icons
from .paths import image_dir
from kdesk.hourglass import hourglass_start, hourglass_end

app_profiles = read_json(app_profiles_file)


# The list of the displayed items
class ProjectList():
    def __init__(self):
        self.width = 646
        self.height = 88

        apps = get_app_list()

        self.projects_list = []

        for app in apps:
            if app in app_profiles:
                if 'ext' in app_profiles[app]:
                    if app_profiles[app]['dir'] == 'kanoprofile':
                        data_dir = get_app_data_dir(app)
                    else:
                        data_dir = os.path.join(get_home(), app_profiles[app]['dir'])

                    icon_path = os.path.join(image_dir, 'icons', app_profiles[app]['icon'])

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
        self.background.get_style_context().add_class('project_list_background')

        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.align = Gtk.Alignment(xalign=0.5, yalign=0.5)
        self.align.set_padding(10, 10, 20, 20)
        self.align.add(self.container)
        self.background.add(self.align)

        if not self.projects_list:
            image_no_projects = icons.set_from_name('no_challenges')
            image_no_projects.set_margin_top(70)
            self.container.pack_start(image_no_projects, False, False, 0)
            return

        for i, project in enumerate(self.projects_list):
            item = ProjectItem(project)
            self.container.pack_start(item.background, False, False, 0)


# Each item shown in the list
class ProjectItem():
    def __init__(self, project):
        self.background = Gtk.EventBox()
        self.background.get_style_context().add_class('white')

        self.button = Gtk.Button(_("MAKE"))
        self.button.connect('clicked', self.load, project['app'], project['file'], project['data_dir'])
        self.button.get_style_context().add_class('project_make_button')
        cursor.attach_cursor_events(self.button)
        self.button_padding = Gtk.Alignment(xscale=1, yscale=1, xalign=0.5, yalign=0.5)
        self.button_padding.set_padding(25, 25, 10, 10)
        self.button_padding.add(self.button)

        # shorten project name to 20 characters long
        display_name = project['display_name']
        if len(display_name) > 20:
            display_name = display_name[:20] + u'…'

        self.title = Gtk.Label(display_name)
        self.title.get_style_context().add_class('project_item_title')
        self.title.set_alignment(xalign=0, yalign=1)

        self.label_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.label_container.pack_start(self.title, False, False, 0)

        self.label_align = Gtk.Alignment(xalign=0, yalign=0.5, xscale=1, yscale=0)
        self.label_align.add(self.label_container)
        self.label_align.set_padding(0, 0, 10, 0)

        self.image = Gtk.Image()
        self.image.set_from_file(project['icon'])

        self.container = Gtk.Box()
        self.container.pack_start(self.image, False, False, 0)
        self.container.pack_start(self.label_align, False, False, 0)
        self.container.pack_end(self.button_padding, False, False, 0)

        self.background.add(self.container)

    def load(self, _button, app, filename, data_dir):
        hourglass_start(app)
        rc = launch_project(app, filename, data_dir)
        if not rc == 0:
            hourglass_end()

    def share(self, _button, app, filename):
        logger.info("share: {} {}".format(app, filename))


def activate(_win):
    project_list = ProjectList()

    scrolledwindow = ScrolledWindow()
    scrolledwindow.apply_styling_to_widget()
    scrolledwindow.add_with_viewport(project_list.background)
    scrolledwindow.set_size_request(734, 404)

    _box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    _box.pack_start(scrolledwindow, False, False, 0)

    _win.pack_in_main_content(_box)
    _win.show_all()
