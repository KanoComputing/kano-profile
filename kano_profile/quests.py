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
from kano_profile_gui.paths import media_dir

QUESTS_LOAD_PATHS = [
    '/usr/share/kano-profile/quests',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '../quests')
]
QUESTS_STORE = os.path.join(profile_dir, 'quests.json')


# Breaking the Quest API? Make sure to bump this number.
#
# Bump the major version if you're making an backwards incompatible change
# and the minor one if the feature is backwards compatible.
#
API_VERSION = {'major': 1, 'minor': 1}


def api_version(version):
    """
        Request a certain version of the API.

        :param version: The requested version of the API.
        :type version: dict

        :raises RuntimeError: If the request cannot be satisfied.
        :returns: None
    """

    if ('major' in version and version['major'] != API_VERSION['major']) or \
       ('minor' in version and version['minor'] > API_VERSION['minor']):
        msg = 'Trying to load a quest with incompatible API'
        logger.warn(msg)
        raise RuntimeError(msg)


def profile_media(media_path):
    """
        Get the full path to a media file in profile's directory.

        :param media_path: Relative path to the media file.
        :type media_path: string

        :raises OSError: If the file doesn't exist.
        :returns: The absolute path to the file.
    """

    path = os.path.join(media_dir, media_path)

    if not os.path.exists(path):
        raise OSError("Media file ({}) not found".format(path))
    return path


def quest_media(quest_conf_path, media_path):
    """
        Get the full path to a media file in the quest's directory.

        :param quest_conf_path: The location of the quest's config.py file.
                                Use __file__ when in the file itself.
        :type quest_conf_path: string

        :param media_path: Relative path to the media file.
        :type media_path: string

        :raises OSError: If the file doesn't exist.
        :returns: The absolute path to the file.
    """

    quest_dir = os.path.dirname(os.path.abspath(quest_conf_path))
    path = os.path.join(quest_dir, 'media', media_path)

    if not os.path.exists(path):
        raise OSError("Media file ({}) not found".format(path))
    return path


class Quests(object):
    """
        Manages quest modules.
        It loads them up from different locations and constructs an
        instance for each quest.
    """

    def __init__(self):
        self._quests = []
        self._quest_states = {}

        self._load_system_modules()
        self._load_external_modules()

    def _load_system_modules(self):
        for load_path in QUESTS_LOAD_PATHS:
            if os.path.exists(load_path):
                for f in os.listdir(load_path):
                    full_path = os.path.join(load_path, f, 'quest.py')
                    modname = os.path.basename(os.path.dirname(f))
                    if os.path.isfile(full_path):
                        qmod = imp.load_source(modname, full_path)
                        q = qmod.init()
                        self._quests.append(q(self))
            else:
                logger.warn("'{}' not found".format(load_path))

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
        """
            Returns a quest with the specified id.

            :param qid: The id to look for.
            :type qid: string

            :returns: A `Quest` instance or None.
            :rtype: Quest or None
        """

        for q in self._quests:
            print q.id
            if q.id == qid:
                return q

        return None

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
        self._configure()

    def _configure(self):
        self._title = None
        self._help = None

    def is_fulfilled(self):
        return True

    @property
    def title(self):
        return self._title

    @property
    def help(self):
        return self._help


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
        if self._notification['title'] and self._notification['byline']:
            return self._notification
        else:
            return None


class Badge(Reward):
    def _configure(self):
        super(Badge, self)._configure()

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
        return self._xp

    def _configure(self):
        super(XP, self)._configure()
        self._icon = profile_media('images/icons/xp-reward.png')
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
        self._configure()

        self._load_state()

    def _configure(self):
        self._id = None
        self._icon = None
        self._title = None
        self._description = None
        self._steps = []
        self._rewards = []
        self._depends = []

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
        if os.path.exists(QUESTS_STORE):
            with open(QUESTS_STORE, 'r') as f:
                store = json.load(f)
        else:
            store = {}

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
                if not self.is_fulfilled():
                    self._state = self.ACTIVE

        return self._state not in [self.INACTIVE, self.COMPLETED]

    def is_fulfilled(self):
        """
            Evaluate whether all the steps required to complete the quest
            were fulfulled. If yes, the status of the quest is changed
            to FULFILLED and the status is saved into the quest store.
            :returns: True if fulfilled.
            :rtype: Boolean
        """

        if self._state in [self.FULFILLED, self.COMPLETED]:
            return True

        fulfilled = True
        for step in self._steps:
            fulfilled = fulfilled and step.is_fulfilled()

        if fulfilled:
            self._state = self.FULFILLED
            self._save_state()
        return fulfilled

    def is_completed(self):
        print self._state, self.COMPLETED
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
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def xp(self):
        xps = [r for r in self._rewards if isinstance(r, XP)]
        return reduce(lambda s, xp: s+xp.amount, xps, 0)

    @property
    def badges(self):
        badges = [r for r in self._rewards if issubclass(r.__class__, Badge)]
        return badges

    @property
    def rewards(self):
        return self._rewards
