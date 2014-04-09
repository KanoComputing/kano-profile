#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from ..utils import get_user, get_home_by_username

linux_user = get_user()
home_directory = get_home_by_username(linux_user)

# setting up directories
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
rules_local = os.path.join(dir_path, 'rules')
rules_usr = '/usr/share/kano-profile/rules/'

if os.path.exists(rules_local):
    rules_dir = rules_local
elif os.path.exists(rules_usr):
    rules_dir = rules_usr
else:
    raise Exception('Neither local nor usr rules found!')

# constructing paths of directories, files
kanoprofile_dir_str = '.kanoprofile'
kanoprofile_dir = os.path.join(home_directory, kanoprofile_dir_str)

profile_dir_str = 'profile'
profile_dir = os.path.join(kanoprofile_dir, profile_dir_str)

apps_dir_str = 'apps'
apps_dir = os.path.join(kanoprofile_dir, apps_dir_str)

profile_file_str = 'profile.json'
profile_file = os.path.join(profile_dir, profile_file_str)

xp_file = os.path.join(rules_dir, 'xp.json')
levels_file = os.path.join(rules_dir, 'levels.json')
badges_file = os.path.join(rules_dir, 'badges.json')
