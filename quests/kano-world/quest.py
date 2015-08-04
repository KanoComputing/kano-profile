#
# Kano World Quest configuration
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from kano.network import is_internet
from kano_profile.quests import Quest, XP, Badge, quest_media, Step, \
    api_version
from kano_profile.apps import load_app_state, get_app_list, save_app_state


class WorldExplorerBadge(Badge):
    def _configure(self):
        super(WorldExplorerBadge, self)._configure()

        self._id = 'world-expoler'
        self._dest_locked = 'Kano World Explorer'
        self._desc_unlocked = 'You discovered Kano World!'
        self._icon = quest_media(__file__, 'badge.svg')
        self._image = quest_media(__file__, 'badge.svg')

        n = self._notification
        n['title'] = 'Kano World Explorer'
        n['byline'] = 'You made it to Kano World!'
        n['command'] = 'kano-profile badges'
        n['image'] = quest_media(__file__, 'badge-notification.png')


class Step1(Step):
    def _configure(self):
        self._title = 'Connect to wifi'

    def is_fulfilled(self):
        if is_internet():
            return True
        else:
            return False


class Step2(Step):
    def _configure(self):
        self._title = 'Connect your Kano World account'

    def is_fulfilled(self):
        return True


class Step3(Step):
    def _configure(self):
        self._title = 'Launch the Kano World app'

    def is_fulfilled(self):
        return True


class Step4(Step):
    def _configure(self):
        self._title = 'Like an awesome Kano World share'

    def is_fulfilled(self):
        return True


class KanoWorldQuest(Quest):
    def _configure(self):
        self._id = 'travel-to-kano-world'
        self._title = 'Travel to Kano World'
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

        self._steps = [
            Step1(),
            Step2(),
            Step3(),
            Step4()
        ]
        self._rewards = [
            WorldExplorerBadge(),
            # SpaceSuit(),
            XP(50)
        ]
        self._depends = []


def init():
    api_version({'major': 1, 'minor': 1})
    return KanoWorldQuest
