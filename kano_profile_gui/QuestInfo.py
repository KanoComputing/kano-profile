#!/usr/bin/env python

# QuestInfo.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The show the information about one individual Quest.

import os
from gi.repository import Gtk, GdkPixbuf
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano_profile_gui.paths import css_dir, image_dir
from kano_profile_gui.ProgressDot import ProgressDot


class QuestInfo(Gtk.EventBox):
    css_path = os.path.join(css_dir, "quest_screen.css")
    reward_path = os.path.join(image_dir, "chest.svg")

    def __init__(self, **keywords):
        Gtk.EventBox.__init__(self)
        apply_styling_to_screen(self.css_path)
        self.get_style_context().add_class("quest_screen_background")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)
        self.grid.set_margin_left(10)
        self.grid.set_margin_right(10)
        self.grid.set_margin_bottom(10)
        self.grid.set_margin_top(10)
        vbox.pack_start(self.grid, False, False, 0)

        # May be better elsewhere
        self.win = keywords["win"]
        self.quest = keywords["quest_info"]

        self.win.pack_in_main_content(self)

        # Pack in Progress
        progress_section = self.create_progress_section()
        self.grid.attach(progress_section, 0, 0, 1, 1)

        # Pack in Rewards
        rewards = self.create_reward_section()
        self.grid.attach(rewards, 1, 0, 1, 1)

        # Add the bottom bar
        # bottom_bar = self._create_bottom_navigation_bar()
        # self.win.pack_in_bottom_bar(bottom_bar)

        self.win.show_all()

    def create_progress_section(self):
        scroll_path = os.path.join(image_dir, "scroll.svg")
        scroll_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(scroll_path, 505, -1)
        scroll_img = Gtk.Image.new_from_pixbuf(scroll_pixbuf)

        fixed = Gtk.Fixed()
        fixed.put(scroll_img, 0, 0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_margin_left(10)
        text_background = Gtk.EventBox()
        text_background.add(vbox)
        fixed.put(text_background, 50, 50)
        text_background.set_size_request(405, 350)

        title_label = Gtk.Label(self.quest.title)
        title_label.get_style_context().add_class("quest_info_title")
        title_label.set_alignment(yalign=0.5, xalign=0)

        quest_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.quest.icon, 80, 80)
        quest_image = Gtk.Image.new_from_pixbuf(quest_pixbuf)

        header_box = Gtk.Box()
        header_box.pack_start(quest_image, False, False, 5)
        header_box.pack_start(title_label, False, False, 5)
        header_box.set_margin_top(10)
        header_box.set_margin_left(10)

        vbox.pack_start(header_box, True, False, 0)

        steps = self.quest.steps
        self.progress_dots = []

        for step in steps:
            quest_step_label = Gtk.Label(step.title)

            fulfilled = step.is_fulfilled()
            progress_dot = ProgressDot(fulfilled)
            self.progress_dots.append(progress_dot)
            quest_step_label.get_style_context().add_class("quest_step_label")

            if fulfilled:
                quest_step_label.get_style_context().add_class("fulfilled")

            # Pack each section
            hbox = Gtk.Box()
            hbox.pack_start(progress_dot, False, False, 5)
            hbox.pack_start(quest_step_label, False, False, 5)
            vbox.pack_start(hbox, True, False, 0)

        return fixed

    def create_reward_section(self):
        background = Gtk.EventBox()
        background.get_style_context().add_class("quest_section")
        background.get_style_context().add_class("reward_background")
        background.set_size_request(100, -1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        background.add(vbox)

        title = Gtk.Label("Rewards")
        title.set_alignment(xalign=0, yalign=0.5)
        title.set_padding(xpad=10, ypad=10)
        title.get_style_context().add_class("reward_title")
        grid = Gtk.Grid()
        grid.set_margin_left(20)
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)

        vbox.pack_start(title, False, False, 0)
        vbox.pack_start(grid, False, False, 0)

        left = 0
        top = 0
        max_columns = 1

        rewards = self.quest.rewards

        for reward in rewards:
            reward_widget = self.create_reward(
                reward.title, reward.icon
            )
            grid.attach(reward_widget, left, top, 1, 1)
            left += 1

            if left >= max_columns:
                left = 0
                top += 1

        return background

    def create_reward(self, title, path):
        # Add hover over effect
        background = Gtk.EventBox()
        background.get_style_context().add_class("quest_section")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        background.add(vbox)

        # For now, use default
        label = Gtk.Label(title)
        label.set_line_wrap(True)
        label.get_style_context().add_class("reward_label")

        if path and os.path.exists(path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, 120, 120)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            vbox.pack_start(image, False, False, 5)

        vbox.pack_start(label, False, False, 5)
        return background

    # Currently not used
    '''
    def create_quest_description(self):
        sw = ScrolledWindow()
        sw.apply_styling_to_widget()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.set_size_request(200, 150)
        sw.get_style_context().add_class("quest_section")

        desc_background = Gtk.EventBox()
        desc_background.set_margin_top(10)
        desc_background.set_margin_left(10)
        sw.add(desc_background)

        title_label = Gtk.Label("Quest Info")
        title_label.get_style_context().add_class("quest_info_title")
        title_label.set_alignment(xalign=0, yalign=0.5)

        desc_label = Gtk.Label(self.quest._description)
        desc_label.get_style_context().add_class("quest_info_description")
        desc_label.set_alignment(xalign=0, yalign=0)
        desc_label.set_line_wrap(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        desc_background.add(vbox)

        vbox.pack_start(title_label, False, False, 0)
        vbox.pack_start(desc_label, False, False, 0)

        return sw

    def _create_bottom_navigation_bar(self):
        navigation_bar = Gtk.EventBox()
        navigation_bar.get_style_context().add_class("quest_section")
        bottom_bar = Gtk.ButtonBox()
        navigation_bar.add(bottom_bar)

        # Do we show these and navigate between the quests this way?
        self.next_button = create_navigation_button(_("Next page").upper(),
                                                    "next")
        # self.next_button.connect("clicked", self._load_page_wrapper, 1)

        self.prev_button = create_navigation_button(_("Previous").upper(),
                                                    "previous")
        # self.prev_button.connect("clicked", self._load_page_wrapper, -1)

        quest_button = create_navigation_button(_("Back to quests").upper(),
                                                "middle")

        bottom_bar.pack_start(self.prev_button, False, False, 0)
        bottom_bar.pack_start(quest_button, False, False, 0)
        bottom_bar.pack_end(self.next_button, False, False, 0)

        return navigation_bar
    '''
