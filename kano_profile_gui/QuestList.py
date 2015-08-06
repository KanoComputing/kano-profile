#!/usr/bin/env python

# QuestList.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The GUI to show the frontend of the Quests.


import os
from gi.repository import Gtk, GObject, GdkPixbuf
from kano_profile_gui.paths import css_dir, image_dir
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano_profile_gui.QuestInfo import QuestInfo
from kano_profile_gui.ProgressDot import Tick


class QuestList(Gtk.EventBox):
    '''
    Screen showing all the Active and Fufilled quests.
    '''
    css_path = os.path.join(css_dir, "quest_screen.css")

    def __init__(self, win):
        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class("quest_screen_background")

        self.checked_quests = False
        self.win = win
        self.win.pack_in_main_content(self)

        # Apply the styling from the Quests file
        apply_styling_to_screen(self.css_path)
        self.display_quests()

    def display_quests(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Calculate the quests that are available.
        for quest in self.win.quests.list_active_quests():
            quest_item = QuestListItem(win=self.win, quest_info=quest)
            vbox.pack_start(quest_item, False, False, 10)
            quest_item.connect("reward_claimed", self.repack_quests)

        self.show_all()

    def repack_quests(self, widget=None):

        # Unpack quests
        for child in self.get_children():
            self.remove(child)

        self.display_quests()


class QuestListItem(Gtk.Fixed):
    '''This shows a Quest button packed into the QuestScreen
    '''

    __gsignals__ = {
        'reward_claimed': (GObject.SIGNAL_RUN_FIRST, None, ())
    }
    width = 710
    height = 130

    def __init__(self, win, quest_info):

        self.win = win
        self.quest_info = quest_info

        Gtk.Fixed.__init__(self)
        self.set_size_request(self.width, self.height)

        self.background = Gtk.EventBox()
        self.background.get_style_context().add_class("quest")
        self.background.set_margin_left(10)
        self.background.set_size_request(self.width, self.height)
        self.put(self.background, 0, 0)

        title = quest_info.title
        self.title_widget = Gtk.Label(title)
        self.title_widget.get_style_context().add_class("quest_item_title")
        self.title_widget.set_alignment(xalign=0, yalign=1)

        fulfilled = quest_info.is_fulfilled()

        if fulfilled:
            # Put shine on the QuestMenuItem
            path = os.path.join(image_dir, "quests/completed-quest-bar-shine.svg")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                path, self.width, self.height
            )
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            self.background.add(image)

            self.title_widget.get_style_context().add_class("fulfilled")
            self.background.get_style_context().add_class("fulfilled")
            icon_path = self.quest_info.fulfilled_icon
        else:
            self.background.get_style_context().add_class("not_fulfilled")
            icon_path = self.quest_info.icon

        # This is so the widgets are stacked properly on top of each other
        transparent_background = Gtk.EventBox()
        transparent_background.connect(
            "enter-notify-event", self.hover_over_effect, True
        )
        transparent_background.connect(
            "leave-notify-event", self.hover_over_effect, False
        )
        hbox = Gtk.Box()
        hbox.set_size_request(self.width, self.height)
        transparent_background.add(hbox)
        self.put(transparent_background, 0, 0)

        quest_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            icon_path, 120, 120
        )
        quest_icon = Gtk.Image.new_from_pixbuf(quest_pixbuf)
        quest_icon.set_margin_left(20)
        quest_icon.set_margin_top(10)
        quest_icon.set_margin_bottom(10)

        # Get text for the reward_list_widget
        reward_text = "Rewards: "
        tick_box = Gtk.Box()

        for reward in self.quest_info.rewards:
            reward_text += reward.title

            if not reward == self.quest_info.rewards[-1]:
                reward_text += ", "

        tick_width = 30
        tick_height = 30
        for step in self.quest_info.steps:

            # If the whole quest has been completed,
            # make all the ticks gold
            if self.quest_info.is_fulfilled():
                tick = Tick(
                    width=tick_width,
                    height=tick_height,
                    color="gold"
                )

            # If the individual step has been completed,
            # make all tick orange
            elif step.is_fulfilled():
                tick = Tick(
                    width=tick_width,
                    height=tick_height,
                    color="orange"
                )

            # uncompleted steps should have a grey tick
            else:
                tick = Tick(
                    width=tick_width,
                    height=tick_height,
                    color="grey"
                )
            tick_box.pack_start(tick, False, False, 5)

        self.reward_list_label = Gtk.Label(reward_text)
        self.reward_list_label.set_alignment(xalign=0, yalign=0)
        self.reward_list_label.get_style_context().add_class(
            "quest_item_rewards"
        )
        if fulfilled:
            self.reward_list_label.get_style_context().add_class("fulfilled")

        quest_text_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        quest_text_vbox.pack_start(self.title_widget, True, True, 0)
        quest_text_vbox.pack_start(self.reward_list_label, True, True, 0)

        # Pack in all the widgets.
        hbox.pack_start(quest_icon, False, False, 10)
        hbox.pack_start(quest_text_vbox, True, True, 10)

        if fulfilled:
            self.connect("button-release-event", self.claim_reward)

            # Create a rosette and pack at the end
            path = os.path.join(image_dir, "quests/rosette-complete.svg")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, 80, 80)
            rosette = Gtk.Image.new_from_pixbuf(pixbuf)
            hbox.pack_end(rosette, False, False, 10)
        else:
            tick_box.set_margin_right(20)
            self.connect("button-release-event", self.go_to_quest_info)

        hbox.pack_end(tick_box, False, False, 10)

    def hover_over_effect(self, widget, event, hover):
        if hover:
            style_context = self.background.get_style_context()
            if "hover" not in style_context.list_classes():
                style_context.add_class("hover")
        else:
            self.background.get_style_context().remove_class("hover")

    def claim_reward(self, widget=None, event=None):

        # TODO: this feels quite hacky. Should be moved back to the MenuBar
        # class, and maybe use signals instead?
        menu_bar = self.win.menu_bar
        quest_button = menu_bar.get_button("QUESTS")

        # Update the quest button
        quest_button.check_for_notification()

        # Unpack current reward and reshow new quests
        self.emit("reward_claimed")

    def go_to_quest_info(self, button=None, event=None):
        self.win.empty_main_content()
        QuestInfo(win=self.win, quest_info=self.quest_info)
