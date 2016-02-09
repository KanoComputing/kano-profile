import os

try:
    from unittest.mock import patch  # In Python 3, mock is built-in
except ImportError:
    from mock import patch  # Python 2

import pyfakefs.fake_filesystem_unittest

from tests.profile.rules import RULES_SETUP
from tests.profile.utils import parse_badges

from kano_profile.badges import calculate_xp, calculate_app_progress, \
    calculate_badges


class EnsureAppProfile(pyfakefs.fake_filesystem_unittest.TestCase):
    APP = ''
    PROFILE = None
    EXPECTED_XP = 0
    EXPECTED_PROGRESS = 0
    EXPECTED_BADGES = []

    def setUp(self):
        self.setUpPyfakefs()

        for installed_path, local_path, contents in RULES_SETUP:
            '''
            self.fs.CreateFile(
                installed_path,
                contents=contents
            )
            '''
            self.fs.CreateFile(
                local_path,
                contents=contents
            )

        self.fs.CreateFile(
            os.path.expanduser(
                '~/.kanoprofile/apps/{}/state.json'.format(self.APP)
            ),
            contents=self.PROFILE
        )

    def test_app_progress(self):
        self.assertEqual(calculate_app_progress(self.APP),
                         self.EXPECTED_PROGRESS)

    def test_badge_calculation(self):
        awards = calculate_badges()
        badges = parse_badges(awards['badges'])

        self.assertEqual(sorted(badges), sorted(self.EXPECTED_BADGES))

    def test_xp_calculation(self):
        self.assertEqual(calculate_xp(), self.EXPECTED_XP)
