#
# Kano World Quest configuration
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from kano.network import is_internet
from kano_profile.quests import Quest, XP, Badge, quest_media, Step, \
    CharacterAsset

class KanoWorldBadge(Badge):
    def _configure(self):
        self._title = 'Kano World Explorer'
        self._icon = quest_media('badge-icon.png')

        n = self._notification
        n['title'] = 'Kano World Explorer'
        n['byline'] = 'You made it to Kano World!'
        n['command'] = 'kano-profile badges'
        n['image'] = quest_media('badge-notification.png')


class SpaceSuit(CharacterAsset):
    pass


class Step1(Step):
    def _configure(self):
        self._title = 'Connect to wifi'

    def is_completed(self):
        if is_internet():
            return True
        else:
            return False


class KanoWorldQuest(Quest):
    def _configure(self):
        self._name = 'kano-world'
        self._title = 'Fly to Kano World'
        self.description = """
Godard distillery bitters dreamcatcher butcher, pop-up irony Austin scenester
narwhal retro raw denim. Irony pork belly slow-carb seitan Austin. Mlkshk
plaid Neutra, quinoa tattooed bitters Odd Future paleo Helvetica next level
crucifix High Life flannel VHS. Pour-over Austin paleo umami. Deep v small
batch mustache, fap polaroid try-hard biodiesel dreamcatcher wayfarers butcher
Schlitz you probably haven't heard of them. Odd Future lumbersexual umami
hella fap you probably haven't heard of them American Apparel, paleo wolf
whatever readymade farm-to-table. Thundercats Pitchfork brunch drinking
vinegar, four loko fashion axe polaroid freegan trust fund scenester meggings
semiotics keytar vegan. """


        self.steps = [
            Step1(),
            Step2(),
            Step3()
        ]
        self._rewards = [
            KanoWorldBadge(),
            SpaceSuit(),
            XP(50)
        ]
        self._depends = []
