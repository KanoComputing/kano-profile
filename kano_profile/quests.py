# quests.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import json
import imp

from kano.logging import logger
from kano.utils import ensure_dir
from .paths import profile_dir
from .apps import load_app_state, get_app_list, save_app_state


QUESTS_LOAD_PATH = "/usr/share/kano-profile/quests"
QUESTS_STORE = os.path.join(profile_dir, 'quests.json')


# Breaking the Quest API? Make sure to bump this number.
#
# Bump the major version if you're making an backwards incompatible change
# and the minor one if the feature is backwards compatible.
#
API_VERSION = {'major': 1, 'minor': 1}


class NotConfiguredError(Exception):
    pass


class Quests(object):
    """
        Manages quest modules.

        It loads them up from different locations and constructs an
        instance for each quest.
    """

    def __init__(self):
        self._quests = []
        self._quest_states = {}

    def _load_system_modules(self):
        for f in os.listdir(QUESTS_LOAD_PATH):
            full_path = os.path.join(QUESTS_LOAD_PATH, f)
            modname = os.path.basename(os.path.dirname(f))
            if os.path.isfile(full_path):
                qmod = imp.load_source(modname, full_path)
                q = qmod.init()
                if q.api_version['major'] == API_VERSION['major'] and \
                   q.api_version['minor'] <= API_VERSION['minor']:
                    self._quests.append(q)
                else:
                    logger.warn("Trying to load a quest with incompatible API")

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

    def get_quest(self, qid):
        if qid not in self._quests:
            return None

        return self._quests[qid]

    def evaluate_xp(self):
        xp = 0
        for quest in self._quests:
            if quest.is_completed():
                xp += quest.xp

        return xp

    def evaluate_badges(self):
        badges = []
        for quest in self._quests:
            if quest.is_completed():
                badges += quest.badges

        return badges


class Step(object):
    """
        Represents one step towards completing a quest.

        This is just a base class. Needs to be implemented by the quest.
    """

    def __init__(self):
        pass

    def _configure(self):
        self._title = None
        self._help = None

    def is_fulfilled(self):
        return True


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

    @property
    def icon(self):
        return self._icon

    @property
    def title(self):
        return self._title

    @property
    def notification(self):
        if self._notification['title'] is not None and \
           self._notification['byline'] is not None:
            return self._notification
        else:
            return None


class Badge(Reward):
    def _configure(self):
        super(Badge, self)._configure(self)

        # _title and _icon inherited from reward

        self._id = None
        self._desc_locked = None
        self._desc_unlocked = None
        self._image = None

    @property
    def id(self):
        return self._id

    @property
    def desc_locked(self):
        return self._desc_locked

    @property
    def desc_unlocked(self):
        return self._desc_unlocked

    @property
    def image(self):
        return self._image


class XP(Reward):
    def __init__(self, amount):
        self._xp = amount
        super(XP, self).__init__()

    @property
    def amount(self):
        return self._amount

    def _configure(self):
        self._icon = None
        self._title = None


class QuestError(Exception):
    pass


class Quest(object):
    """
        A base class for each quest.
    """

    INACTIVE = 'inactive'
    ACTIVE = 'active'
    FULFILLED = 'fulfilled'
    COMPLETED = 'completed'

    def __init__(self, manager):
        self._manager = manager
        self._path = os.path.dirname(os.path.abspath(__file__))
        self._state = self.INACTIVE
        self._req_api_version = None
        self._configure()

        if self._req_api_version is None:
            raise QuestError('req_api_version must be set!')

        self._load_quest_state()

    def _configure(self):
        self._id = None
        self._icon = None
        self._title = None
        self._description = None
        self._steps = []
        self._depends = []

    def _get_media(self, media_path):
        return os.path.join(self._path, 'media', media_path)

    def _load_state(self):
        if os.path.exists(QUESTS_STORE):
            with open(QUESTS_STORE, 'r') as f:
                store = json.load(f)
        else:
            store = {}

        if self._id in store:
            self._state = store[self._id]['state']

    def _save_state(self):
        ensure_dir(os.path.dirname(QUESTS_STORE))
        with open(QUESTS_STORE, 'r') as f:
            store = json.load(f)

        if self._id not in store:
            store[self._id] = {}
        store[self._id]['state'] = self._state

        with open(QUESTS_STORE, 'w') as f:
            json.dump(store, f)

    def _can_be_active(self):
        active = True
        for dep_id in self._depends:
            quest = self._manager.get_quest(dep_id)
            active = active and quest.is_completed()
        return active

    def is_active(self):
        if self._state == self.INACTIVE:
            if self._can_be_active():
                if not self.evaluate_fulfilment():
                    self._state = self.ACTIVE

        return self._state not in [self.ACTIVE, self.FULFILLED]

    def is_fulfilled(self):
        """
            Evaluate whether all the steps required to complete the quest
            were fulfulled. If yes, the status of the quest is changed
            to FULFILLED and the status is saved into the quest store.

            :returns: True if fulfilled.
            :rtype: Boolean
        """

        fulfilled = True
        for step in self._steps:
            fulfilled = fulfilled and step.is_fulfilled()

        if fulfilled:
            self._state = self.FULFILLED
            self._save_state()
        return fulfilled

    def is_completed(self):
        return self._state == self.COMPLETED

    def mark_completed(self):
        """
            Mark a fulfilled quest complete to claim the reward.

            This will set the state of the quest to COMPLETED in the quest
            store.

            :raises QuestError: If the quest isn't ready to be marked complete.
        """

        if self.is_fulfilled():
            self._state = self.COMPLETED
            self._save_state()
        else:
            raise QuestError('Quest not ready to be completed.')

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def xp(self):
        xps = [r for r in self._rewards if isinstance(r, XP)]
        return reduce(lambda s, xp: s+xp.amount(), xps, 0)

    @property
    def badges(self):
        badges = [r for r in self._rewards if isinstance(r, Badge)]
        return reduce(lambda lst, b: lst.append(b), badges, [])

    @property
    def rewards(self):
        return self._rewards
