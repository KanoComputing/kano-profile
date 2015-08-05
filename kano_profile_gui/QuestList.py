#!/usr/bin/env python

# QuestList.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The GUI to show the frontend of the Quests.


import os
from gi.repository import Gtk, GObject, GdkPixbuf
from kano_profile_gui.paths import image_dir, css_dir
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano_profile_gui.QuestInfo import QuestInfo


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
            vbox.pack_start(quest_item, False, False, 0)
            quest_item.connect("reward_claimed", self.repack_quests)

        self.show_all()

    def repack_quests(self, widget=None):

        # Unpack quests
        for child in self.get_children():
            self.remove(child)

        self.display_quests()


class QuestListItem(Gtk.EventBox):
    '''This shows a Quest button packed into the QuestScreen
    '''

    __gsignals__ = {
        'reward_claimed': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    # Placeholders
    reward_path = os.path.join(image_dir, "chest.svg")

    def __init__(self, win, quest_info):

        self.win = win
        self.quest_info = quest_info

        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class("quest_section")

        # Add hover over effects - these could be added to CSS if the widget
        # is a Gtk.Button
        self.connect("enter-notify-event", self.hover_over_effect, True)
        self.connect("leave-notify-event", self.hover_over_effect, False)
        self.set_size_request(-1, 100)
        self.get_style_context().add_class("quest")

        fulfilled = quest_info.is_fulfilled()
        title = quest_info.title

        if fulfilled:
            self.get_style_context().add_class("fulfilled")
        else:
            self.get_style_context().add_class("not_fulfilled")

        hbox = Gtk.Box()
        self.add(hbox)

        quest_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            self.quest_info.icon, 100, 100
        )
        quest_icon = Gtk.Image.new_from_pixbuf(quest_pixbuf)
        quest_icon.set_margin_left(10)

        self.title_widget = Gtk.Label(title)
        self.title_widget.get_style_context().add_class("quest_item_title")
        self.title_widget.set_alignment(xalign=0, yalign=1)

        # Get text for the reward_list_widget
        reward_text = "Rewards: "
        for reward in self.quest_info.rewards:
            reward_text += reward.title

            if not reward == self.quest_info.rewards[-1]:
                reward_text += ", "

        self.reward_list_label = Gtk.Label(reward_text)
        self.reward_list_label.set_alignment(xalign=0, yalign=0)
        self.reward_list_label.get_style_context().add_class("quest_item_rewards")

        quest_text_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        quest_text_vbox.pack_start(self.title_widget, True, True, 0)
        quest_text_vbox.pack_start(self.reward_list_label, True, True, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.reward_path, 40, 40)
        reward_image = Gtk.Image.new_from_pixbuf(pixbuf)

        # Pack in all the widgets.
        hbox.pack_start(quest_icon, False, False, 0)
        hbox.pack_start(quest_text_vbox, True, False, 10)

        if fulfilled:
            self.connect("button-release-event", self.claim_reward)
        else:
            self.connect("button-release-event", self.go_to_quest_info)

        reward_image.set_margin_right(10)
        hbox.pack_end(reward_image, False, False, 0)

    def hover_over_effect(self, widget, event, hover):

        if hover:
            style_context = self.get_style_context()
            if "hover" not in style_context.list_classes():
                style_context.add_class("hover")
        else:
            self.get_style_context().remove_class("hover")

    def claim_reward(self, widget=None, event=None):

        # TODO: this feels quite hacky. Should be moved back to the MenuBar
        # class, and maybe use signals instead?
        menu_bar = self.win._menu_bar
        quest_button = menu_bar.get_button("QUESTS")

        # Update the quest button
        quest_button.check_for_notification()

        # Unpack current reward and reshow new quests
        self.emit("reward_claimed")

    def go_to_quest_info(self, button=None, event=None):
        self.win.empty_main_content()
        QuestInfo(win=self.win, quest_info=self.quest_info)
