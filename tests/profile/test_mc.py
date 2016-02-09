#
# test_mc.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This module tests the calculation of XP and badges for Make Minecraft
#

from tests.profile.paths import get_profile_data
import tests.profile.ensure_app_profile


APP = 'make-minecraft'
PROFILE_DATA = get_profile_data(APP)

class EnsureEmptyProfile(tests.profile.ensure_app_profile.EnsureAppProfile):
    APP = APP
    PROFILE = PROFILE_DATA['empty']
    EXPECTED_XP = 0
    EXPECTED_PROGRESS = 0
    EXPECTED_BADGES = []


class EnsureCompleteProfile(tests.profile.ensure_app_profile.EnsureAppProfile):
    APP = APP
    PROFILE = PROFILE_DATA['complete']
    EXPECTED_XP = 500
    EXPECTED_PROGRESS = 13
    EXPECTED_BADGES = [
        'block_builder',
        'amazing_architect',
        'minecraft_master',
        '100_blocks',
        '1000_blocks',
        'first_challenge',
        '5_challenges',
        '10_challenges'
    ]
