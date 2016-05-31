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
    reward_path = os.path.join(image_dir, "quests/chest.svg")

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

        self.win.show_all()

    def create_progress_section(self):
        scroll_path = os.path.join(image_dir, "quests/scroll.svg")
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
        background.set_size_request(140, -1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        background.add(vbox)

        title = Gtk.Label(_("Rewards"))
        title.set_alignment(xalign=0.5, yalign=0.5)
        title.set_padding(xpad=10, ypad=10)
        title.get_style_context().add_class("reward_title")
        vbox.pack_start(title, False, False, 10)

        for reward in self.quest.rewards:
            reward_widget = self.create_reward(
                reward.title, reward.icon
            )
            vbox.pack_start(reward_widget, False, False, 0)

        return background

    def create_reward(self, title, icon):
        return RewardItem(title, icon)


class RewardItem(Gtk.EventBox):
    width = 190
    height = 140
    img_width = 100
    img_height = 100

    def __init__(self, title, path):
        Gtk.EventBox.__init__(self)
        self.set_size_request(self.width, self.height)
        self.connect("enter-notify-event", self.hover_over_effect)
        self.connect("leave-notify-event", self.remove_hover_over)
        self.title = title
        self.fixed = Gtk.Fixed()
        self.add(self.fixed)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.fixed.add(vbox)

        if path and os.path.exists(path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                path, self.img_height, self.img_width
            )

            margin_top = (self.height - self.img_height) / 2
            margin_bottom = margin_top
            margin_left = (self.width - self.img_width) / 2
            margin_right = margin_left

            image = Gtk.Image.new_from_pixbuf(pixbuf)
            image.set_margin_top(margin_top)
            image.set_margin_bottom(margin_bottom)
            image.set_margin_right(margin_right)
            image.set_margin_left(margin_left)
            vbox.pack_start(image, False, False, 0)

    def hover_over_effect(self, widget, event):
        label = Gtk.Label(self.title)
        label.set_line_wrap(True)
        label.get_style_context().add_class("reward_hover_label")

        self.hover_info = Gtk.EventBox()
        self.hover_info.set_size_request(self.width, self.height)
        self.hover_info.get_style_context().add_class("reward_hover_background")
        self.hover_info.add(label)

        self.fixed.put(self.hover_info, 0, 0)
        self.hover_info.show_all()

    def remove_hover_over(self, widget, event):
        self.fixed.remove(self.hover_info)
