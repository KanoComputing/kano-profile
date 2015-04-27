#
# Path constants
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
import os

# Find the local directory which would store the rules and media directory
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Set up the media directory
media_local = os.path.join(dir_path, 'media')
media_usr = '/usr/share/kano-profile/media/'

if os.path.exists(media_local):
    media_dir = media_local
elif os.path.exists(media_usr):
    media_dir = media_usr
else:
    raise Exception('Neither local nor usr media dir found!')

# Set up the rules directory
rules_local = os.path.join(dir_path, 'rules')
rules_usr = '/usr/share/kano-profile/rules/'

if os.path.exists(rules_local):
    rules_dir = rules_local
elif os.path.exists(rules_usr):
    rules_dir = rules_usr
else:
    raise Exception('Neither local nor usr rules dir found!')

AVATAR_SCRATCH = '/tmp/avatar_gen_scratch/avatar.png'
AVATAR_DEFAULT_LOC = '~/avatar-content/'
AVATAR_DEFAULT_NAME = 'avatar.png'

AVATAR_CONF_FILE = os.path.join(rules_dir, 'avatar_generator/conf.yaml')
AVATAR_ASSET_FOLDER = os.path.join(media_dir, 'images/avatar_generator')
CSS_PATH = os.path.join(media_dir, 'CSS/avatar_generator.css')

CHARACTER_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'characters')
ENVIRONMENT_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'environments')
ITEM_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'items')

CATEGORY_ICONS = os.path.join(AVATAR_ASSET_FOLDER, 'category_icons')
ACTIVE_CATEGORY_ICONS = os.path.join(CATEGORY_ICONS, 'active')
INACTIVE_CATEGORY_ICONS = os.path.join(CATEGORY_ICONS, 'inactive')

SPECIAL_CATEGORY_ICONS = os.path.join(AVATAR_ASSET_FOLDER, 'special_category_icons')
ACTIVE_SPECIAL_CATEGORY_ICONS = os.path.join(SPECIAL_CATEGORY_ICONS, 'active')
INACTIVE_SPECIAL_CATEGORY_ICONS = os.path.join(SPECIAL_CATEGORY_ICONS, 'inactive')

PREVIEW_ICONS = os.path.join(AVATAR_ASSET_FOLDER, 'preview')
CIRC_ASSET_MASK = os.path.join(AVATAR_ASSET_FOLDER, 'helper_assets', 'circle_mask.png')
RING_ASSET = os.path.join(AVATAR_ASSET_FOLDER, 'helper_assets', 'grey_ring.png')
PLAIN_MASK = os.path.join(AVATAR_ASSET_FOLDER, 'helper_assets', 'plain_mask.png')
