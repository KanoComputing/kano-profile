#!/usr/bin/env python

# login.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# UI for login screen

from gi.repository import Gtk

from kano.logging import logger

from kano.utils import run_bg
from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.heading import Heading

from kano_profile.paths import bin_dir
from kano_profile.profile import load_profile, save_profile_variable
from kano_world.functions import login as login_, is_registered

from kano_login.templates.labelled_entries import LabelledEntries
from kano_login.templates.top_bar_template import TopBarTemplate
from kano_login.templates.kano_button_box import KanoButtonBox
from kano_login.about_you import AboutYou
from kano_login.data import get_data

profile = load_profile()
force_login = is_registered() and 'kanoworld_username' in profile


class Login(TopBarTemplate):
    data = get_data("LOGIN")

    def __init__(self, win):

        TopBarTemplate.__init__(self)
        self.win = win
        self.win.add(self)

        self.heading = Heading(self.data["LABEL_1"], self.data["LABEL_2"])
        self.box.pack_start(self.heading.container, False, False, 10)

        self.labelled_entries = LabelledEntries([{"heading": "Username", "subheading": ""}, {"heading": "Password", "subheading": ""}])
        self.labelled_entries.get_entry(1).set_visibility(False)
        self.box.pack_start(self.labelled_entries, False, False, 15)

        self.button_box = KanoButtonBox("LOGIN", "Create New")
        self.box.pack_start(self.button_box, False, False, 30)

        self.button_box.kano_button.connect("button_release_event", self.log_user_in)
        self.button_box.kano_button.connect("key-release-event", self.log_user_in_key)
        self.button_box.set_orange_button_cb(self.create_new)

        self.win.show_all()

    def create_new(self, widget, event, args=[]):
        self.win.clear_win()
        AboutYou(self.win)

    def log_user_in_key(self, widget, event):
        # 65293 is the ENTER keycode.
        if event.keyval == 65293:
            self.log_user_in(widget, event)

    def log_user_in(self, widget, event):
        self.button_box.kano_button.set_sensitive(False)
        [username_email, password_text] = self.labelled_entries.get_entry_text()
        success, text = login_(username_email, password_text)

        if not success:
            logger.info('problem with login: {}'.format(text))
            kdialog = KanoDialog("Houston, we have a problem", text)
            kdialog.run()

        else:
            logger.info('login successful')

            # restore on first successful login/restore
            first_sync_done = False
            try:
                first_sync_done = profile['first_sync_done']
            except Exception:
                pass

            if not first_sync_done:
                logger.info('running kano-sync --sync && --sync && --restore after first time login')

                # doing first sync and restore
                cmd1 = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
                cmd2 = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
                cmd3 = '{bin_dir}/kano-sync --restore -s'.format(bin_dir=bin_dir)
                cmd = "{} && {} && {}".format(cmd1, cmd2, cmd3)
                run_bg(cmd)

                save_profile_variable('first_sync_done', True)

            else:
                logger.info('running kano-sync --sync after non-first login')

                # sync on each successful login
                cmd = '{bin_dir}/kano-sync --sync -s'.format(bin_dir=bin_dir)
                run_bg(cmd)

            kdialog = KanoDialog("Success!", "You're in - online features now enabled")
            response = kdialog.run()
            # Default response
            if response == 0:
                Gtk.main_quit()

        self.button_box.kano_button.set_sensitive(True)
