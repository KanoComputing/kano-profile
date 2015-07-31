# quests.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import json
import imp
import 

from kano.logging import logger
from kano.utils import read_json, is_gui, is_running, run_bg
from .paths import xp_file, levels_file, rules_dir, bin_dir, \
    app_profiles_file, online_badges_dir, online_badges_file
from .apps import load_app_state, get_app_list, save_app_state


QUESTS_LOAD_PATH = "/usr/share/kano-profile/quests"

class Quests(object):
    """
        Manages quest modules.

        It loads them up from different locations and constructs an
        instance for each quest.
    """

    def __init__(self):
        self._quests = []

    def _load_system_modules(self):
        module_files = []
        for f in os.listdir(QUESTS_LOAD_PATH):
            full_path = os.path.join(QUESTS_LOAD_PATH, f)
            modname = os.path.basename(f)
            if os.path.isfile(full_path):
                qmod = imp.load_source(modname, full_path)
                self._quests.append(qmod.init())


    def _load_external_modules(self):
        """
            TODO: This needs to be populated from kano-content
        """
        pass

    def list_quests(self):
        return self._quests

    def list_active_quests(self):
        """
            Active quest is one that should be displayed in the UI and that
            can be worked on by the user.

            Currently, active quests are those ones that have all their
            dependencies completed, but haven't been completed themselves.
        """

        active = []
        for quest in self._quests:
            if quest.is_active():
                active.append(quest)

        return active

    def get_quest(name):
        pass

    def evaluate_xp(self):
        xp = 0
        for quest in self._quests:
            if quest.is_completed():
                xp += quest.get_xp()

        return xp

    def evaluate_badges(self):
        badges = []
        for quest in self._quests:
            if quest.is_completed():
                badges += quest.get_badges()

        return badges


class Step(object):
    """
        Represents one step towards completing a quest.

        This is just a base class. Needs to be implemented by the quest.
    """

    def __init__(self):
        self._title = None
        self._help = None

    def is_completed(self):
        pass


class Reward(object):
    """
        Represents an object (badge, environment, avatar asset and anything
        else) that can be rewarded for a quest. It has to have a short name
        and an icon to be displayed in the quest menu.
    """

    def __init__(self):
        self._configure()

    def _configure(self):
        self._icon = None
        self._title = None

        self._notification = n = {}
        n['title'] = None
        n['byline'] = None
        n['command'] = None
        n['image'] = None

    def get_notification(self):
        if self._notification['title'] != None and
           self._notification['byline'] != None:
            return self._notification
        else:
            return None


class Badge(Reward):
    def _configure(self):
        super(Badge, self)._configure(self)

        self._name = None
        self._description = None
        self._image = None

class XP(Reward):
    def __init__(self, amount):
        self._xp = amount
        super(XP, self).__init__()

    def _configure(self):
        self._icon = ..
        self._title

class Quest(object):
    """
        A base class for each quest.
    """

    INACTIVE = 'inactive'
    IN_PROGRESS = 'in-progress'
    FULFILLED = 'fulfilled'
    COMPLETED = 'completed'

    def __init__(self, manager):
        self._manager = manager
        self._state = INACTIVE # ACTIVE, FULLFILED, COMPLETED
                               # This needs to be loaded from user profile
        self._configure()

    def self._configure(self):
        self._name = None
        self._title = None
        self._description = None
        self._steps = []
        self._depends = []

    def is_completed(self):
        completed = True
        for step in self._steps:
            completed = completed and step.is_completed()
        return completed

    def is_active(self):
        active = True
        for dep_name in self._depends:
            quest = self._manager.get_quest(dep_name)
            active = active and quest.is_completed()
        return active

    def get_xp(self):
        return self._xp

    def get_badges(self):
        return self._badges
