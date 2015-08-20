
# Kano World Quest configuration
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from kano_profile.quests import Quest, XP, Badge, quest_media, Step, \
    api_version
from kano_profile.apps import load_app_state_variable


class HackerBadge(Badge):
    def _configure(self):
        super(HackerBadge, self)._configure()

        self._id = 'hack-the-internet'
        self._title = title = 'Hipster Hacker'
        self._icon = quest_media(__file__, 'badge.svg')

        self._desc_locked = title
        self._desc_unlocked = 'You did it!'
        self._bg_color = 'ffe591'
        self._image = self._icon
        self._image_locked = self._icon

        n = self._notification
        n['title'] = title
        n['byline'] = 'You made it to Kano World!'
        n['command'] = 'kano-profile badges'
        n['image'] = quest_media(__file__, 'badge-notification.png')


class Step1(Step):
    def _configure(self):
        super(Step1, self)._configure()
        self._title = 'Hack kano website'

        self._events = [
            'hack-kano-website'
        ]

    def is_fulfilled(self):
        return False
        return load_app_state_variable('hacker', 'kano-website') == 1


class Step2(Step):
    def _configure(self):
        super(Step2, self)._configure()
        self._title = 'Get the secret code'

        self._events = [
            'hack-code-received'
        ]

    def is_fulfilled(self):
        return False
        return load_app_state_variable('hacker', 'code') == 'judoka'


class HackInternetQuest(Quest):
    def _configure(self):
        super(HackInternetQuest, self)._configure()
        self._id = 'hack-the-internet'
        self._title = 'Hack the internet'
        self._description = """
Godard distillery bitters dreamcatcher butcher, pop-up irony Austin scenester
narwhal retro raw denim. Irony pork belly slow-carb seitan Austin. Mlkshk
plaid Neutra, quinoa tattooed bitters Odd Future paleo Helvetica next level
crucifix High Life flannel VHS. Pour-over Austin paleo umami. Deep v small
batch mustache, fap polaroid try-hard biodiesel dreamcatcher wayfarers butcher
Schlitz you probably haven't heard of them. Odd Future lumbersexual umami
hella fap you probably haven't heard of them American Apparel, paleo wolf
whatever readymade farm-to-table. Thundercats Pitchfork brunch drinking
vinegar, four loko fashion axe polaroid freegan trust fund scenester meggings
semiotics keytar vegan."""

        self._icon = quest_media(__file__, 'quest-icon.svg')
        self._fulfilled_icon = quest_media(__file__, 'quest-icon-completed.svg')

        self._steps = [
            Step1(),
            Step2()
        ]
        self._rewards = [
            HackerBadge(),
            XP(150)
        ]
        self._depends = [
            'travel-to-kano-world'
        ]


def init():
    api_version({'major': 1, 'minor': 1})
    return HackInternetQuest
