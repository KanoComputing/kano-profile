#!/usr/bin/env python

# QuestScreen.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The GUI to show the frontend of the Quests.


import os
from gi.repository import Gtk, GObject, GdkPixbuf
from kano.gtk3.buttons import KanoButton
from kano_profile_gui.paths import image_dir, css_dir
from kano_profile_gui.navigation_buttons import create_navigation_button
from kano.gtk3.apply_styles import apply_styling_to_screen
from kano.gtk3.scrolled_window import ScrolledWindow
from kano_profile.quests import Quests


qm = Quests()


class QuestScreen(Gtk.EventBox):
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
        for quest in qm.list_active_quests():
            indiv_quest = IndividualQuest(win=self.win, quest_info=quest)
            vbox.pack_start(indiv_quest, False, False, 0)
            indiv_quest.connect("reward_claimed", self.repack_quests)

        self.show_all()

    def repack_quests(self, widget=None):

        # Unpack quests
        for child in self.get_children():
            self.remove(child)

        self.display_quests()


class IndividualQuest(Gtk.EventBox):
    '''This shows a Quest button packed into the QuestScreen
    '''

    __gsignals__ = {
        'reward_claimed': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    # Placeholders
    reward_path = os.path.join(image_dir, "chest.svg")
    default_icon_path = os.path.join(image_dir, "icons/snake.png")

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

        completed = quest_info.is_completed()
        title = quest_info.title

        if completed:
            self.get_style_context().add_class("completed")
        else:
            self.get_style_context().add_class("not_completed")

        valign = Gtk.Alignment(yalign=0.5)
        self.add(valign)
        hbox = Gtk.Box()
        valign.add(hbox)

        quest_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            self.quest_info.icon, 100, 100
        )
        quest_icon = Gtk.Image.new_from_pixbuf(quest_pixbuf)
        quest_icon.set_margin_left(10)

        self.title_widget = Gtk.Label(title)
        self.title_widget.get_style_context().add_class("quest_info_title")
        self.title_widget.set_alignment(xalign=0, yalign=0.5)

        # Get text for the reward_list_widget
        reward_text = "Rewards: "
        for reward in self.quest_info.rewards:
            reward_text += reward.title

            if not reward == self.quest_info.rewards[-1]:
                reward_text += ", "

        self.reward_list_widget = Gtk.Label(reward_text)
        self.reward_list_widget.set_alignment(xalign=0, yalign=0.5)
        self.reward_list_widget.get_style_context().add_class("quest_info_rewards")

        quest_text_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        quest_text_vbox.pack_start(self.title_widget, False, False, 0)
        quest_text_vbox.pack_start(self.reward_list_widget, False, False, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.reward_path, 40, 40)
        reward_image = Gtk.Image.new_from_pixbuf(pixbuf)

        if completed:
            # Add CLAIM REWARD button
            self.claim_btn = KanoButton("CLAIM REWARD")
            self.claim_btn.connect("clicked", self.claim_reward)
            self.claim_btn.set_margin_right(10)
            self.claim_btn.set_margin_top(10)
            self.claim_btn.set_margin_bottom(10)

        # Pack in all the widgets.
        hbox.pack_start(quest_icon, False, False, 0)
        hbox.pack_start(quest_text_vbox, False, False, 10)

        if completed:
            self.connect("button-release-event", self.claim_reward)
        else:
            self.connect("button-release-event", self.go_to_individual_quest)

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

    def go_to_individual_quest(self, button=None, event=None):
        self.win.empty_main_content()
        QuestInfoScreen(win=self.win, quest_info=self.quest_info)


##########################################################################
# Widgets used in QuestInfoScreen
##########################################################################


class QuestInfoScreen(Gtk.EventBox):
    css_path = os.path.join(css_dir, "quest_screen.css")

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

        # May be better elsewhere
        self.win = keywords["win"]
        self.quest = keywords["quest_info"]

        self.win.pack_in_main_content(self)

        # Pack in Progress
        progress_section = self.create_progress_section()
        self.grid.attach(progress_section, 0, 0, 1, 2)

        # Pack in Quest Description
        quest_desc = self.create_quest_description()
        self.grid.attach(quest_desc, 1, 0, 1, 1)

        # Pack in Rewards
        rewards = self.create_reward_section()
        self.grid.attach(rewards, 1, 1, 1, 1)

        bottom_bar = self._create_bottom_navigation_bar()

        vbox.pack_start(self.grid, False, False, 0)
        self.win.pack_in_bottom_bar(bottom_bar)
        # vbox.pack_end(navigation_bar, False, False, 0)

        self.win.show_all()

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

    def create_progress_section(self):
        background = Gtk.EventBox()
        background.set_size_request(330, 350)
        background.get_style_context().add_class("quest_section")

        steps = self.quest._steps

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_margin_left(10)
        background.add(vbox)

        title_label = Gtk.Label(self.quest._title)
        title_label.get_style_context().add_class("progress_title")
        title_label.set_alignment(yalign=0.5, xalign=0)

        quest_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.quest.icon, 80, 80)
        quest_image = Gtk.Image.new_from_pixbuf(quest_pixbuf)

        header_box = Gtk.Box()
        header_box.pack_start(quest_image, False, False, 5)
        header_box.pack_start(title_label, False, False, 5)
        header_box.set_margin_top(10)
        header_box.set_margin_left(10)

        vbox.pack_start(header_box, True, False, 0)

        for step in steps:
            quest_step_label = Gtk.Label(step._title)

            fulfilled = step.is_fulfilled()
            progress_dot = ProgressDot(fulfilled)

            if fulfilled:
                quest_step_label.get_style_context().add_class("quest_step_label")

            # Pack each section
            hbox = Gtk.Box()
            hbox.pack_start(progress_dot, False, False, 5)
            hbox.pack_start(quest_step_label, False, False, 5)
            vbox.pack_start(hbox, True, False, 0)

        return background

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

    def create_reward_section(self):
        background = Gtk.EventBox()
        background.get_style_context().add_class("quest_section")
        background.get_style_context().add_class("reward_background")
        background.set_size_request(330, 200)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        background.add(vbox)

        title = Gtk.Label("Rewards")
        title.set_alignment(xalign=0, yalign=0.5)
        title.set_padding(xpad=10, ypad=10)
        title.get_style_context().add_class("rewards_title")
        grid = Gtk.Grid()
        grid.set_margin_left(20)
        grid.set_column_spacing(20)

        vbox.pack_start(title, False, False, 0)
        vbox.pack_start(grid, False, False, 0)

        left = 0
        top = 0
        max_columns = 3

        rewards = self.quest._rewards

        for reward in rewards:
            reward_widget = self.create_reward(
                reward._title, reward._icon
            )
            grid.attach(reward_widget, left, top, 1, 1)
            left += 1

            if left >= max_columns:
                left = 0
                top += 1

        return background

    def create_reward(self, title, path):
        background = Gtk.EventBox()
        background.get_style_context().add_class("quest_section")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        background.add(vbox)

        # For now, use default
        label = Gtk.Label(title)
        label.get_style_context().add_class("reward_title")

        if path and os.path.exists(path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, 40, 40)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            vbox.pack_start(image, False, False, 5)

        vbox.pack_start(label, False, False, 5)
        return background


######################################################################
# Misc classes
######################################################################


class ProgressDot(Gtk.EventBox):
    '''
    A filled or unfilled spot.
    '''

    def __init__(self, filled=False):
        Gtk.EventBox.__init__(self)

        self.get_style_context().add_class("progress_outer_ring")
        self.set_size_request(30, 30)

        align1 = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.5)
        self.add(align1)

        white_ring = Gtk.EventBox()
        white_ring.get_style_context().add_class("progress_white_section")
        white_ring.set_size_request(20, 20)

        align1.add(white_ring)

        align2 = Gtk.Alignment(xscale=0, yscale=0, xalign=0.5, yalign=0.5)
        white_ring.add(align2)

        centre = Gtk.EventBox()
        centre.set_size_request(10, 10)
        align2.add(centre)

        if filled:
            # Fill the centre with green
            centre.get_style_context().add_class("progress_centre_filled")
        else:
            # Fill the centre with white
            centre.get_style_context().add_class("progress_centre_unfilled")


###########################################################################
# TODO: When quests backend becomes active, remove this.
###########################################################################


class FakeQuest2(object):

    def __init__(self):
        self.checked_quests = False

    def get_quests(self):
        '''
        self._name = None
        self._title = None
        self._description = None
        self._steps = []
        self._depends = []
        '''

        if not self.checked_quests:
            self.checked_quests = True

            return [
                {
                    "name": "id1",
                    "title": "Get a Kano World account",
                    "description": "Click on the World icon and create an account.",
                    "steps": [
                        "Step 1",
                        "Step 2",
                        "Step 3"
                    ],
                    "completed": False,
                    "icon_path": os.path.join(image_dir, "icons", "snake.png")
                },
                {
                    "name": "id2",
                    "title": "Connect to internet",
                    "description": "Plug in your WiFi dongle and connect.",
                    "completed": True,
                    "icon_path": os.path.join(image_dir, "icons", "snake.png")
                }
            ]
        else:
            return [
                {
                    "name": "id2",
                    "title": "Get a Kano World account",
                    "description": "Click on the World icon and create an account.",
                    "steps": [
                        "Step 1",
                        "Step 2",
                        "Step 3"
                    ],
                    "completed": False,
                    "icon_path": os.path.join(image_dir, "icons", "snake.png")
                }
            ]
