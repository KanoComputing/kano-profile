# paths.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Path constants for character creation

import os
from kano.utils import get_home, get_user
from kano_content.extended_paths import content_dir

AVATAR_SCRATCH = os.path.join(
    '/tmp/', get_user(), 'char_gen_scratch', 'character.png')
AVATAR_DEFAULT_LOC = os.path.join(get_home(), '.character-content')
AVATAR_DEFAULT_NAME = 'character.png'
AVATAR_ENV_DEFAULT = 'character_inc_env.png'
AVATAR_ENV_SHIFTED = 'character_inc_env_page2.png'
AVATAR_CIRC_PLAIN_DEFAULT = 'character_circ_plain.png'
AVATAR_SELECTED_ITEMS = os.path.join(AVATAR_DEFAULT_LOC, 'character_log.json')
AVATAR_OVERWORLD = os.path.join(get_home(), '.local/share/love/kanoOverworld/res/images/avatar.png')
AVATAR_PONG = os.path.join(get_home(), '.local/share/love/kanoPong/res/images/avatar.png')

AVATAR_CONF_FILE = '/usr/share/kano-profile/rules/avatar_generator/conf.json'
PROFILE_IMAGES_FOLDER = '/usr/share/kano-profile/media/images'
AVATAR_ASSET_FOLDER = os.path.join(PROFILE_IMAGES_FOLDER, 'avatar_generator')
CSS_PATH = '/usr/share/kano-profile/media/CSS/avatar_generator.css'

CHARACTER_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'characters')
CHARACTER_OVERWORLD_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'characters_overworld')
ENVIRONMENT_DIR = os.path.join(
    PROFILE_IMAGES_FOLDER, 'environments', '734x404', 'all')
ITEM_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'items')
ITEM_OVERWORLD_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'items_overworld')

CATEGORY_ICONS = os.path.join(AVATAR_ASSET_FOLDER, 'category_icons')
ACTIVE_CATEGORY_ICONS = os.path.join(CATEGORY_ICONS, 'active')
INACTIVE_CATEGORY_ICONS = os.path.join(CATEGORY_ICONS, 'inactive')

SPECIAL_CATEGORY_ICONS = os.path.join(
    AVATAR_ASSET_FOLDER, 'special_category_icons')
ACTIVE_SPECIAL_CATEGORY_ICONS = os.path.join(SPECIAL_CATEGORY_ICONS, 'active')
INACTIVE_SPECIAL_CATEGORY_ICONS = os.path.join(
    SPECIAL_CATEGORY_ICONS, 'inactive')

PREVIEW_ICONS = os.path.join(AVATAR_ASSET_FOLDER, 'preview')
CIRC_ASSET_MASK = os.path.join(
    AVATAR_ASSET_FOLDER, 'helper_assets', 'circle_mask.png')
RING_ASSET = os.path.join(
    AVATAR_ASSET_FOLDER, 'helper_assets', 'grey_ring.png')
PLAIN_MASK = os.path.join(
    AVATAR_ASSET_FOLDER, 'helper_assets', 'plain_mask.png')

# Register the paths that we will use
content_dir.register_path('ACTIVE_CATEGORY_ICONS', ACTIVE_CATEGORY_ICONS)
content_dir.register_path('INACTIVE_CATEGORY_ICONS', INACTIVE_CATEGORY_ICONS)
content_dir.register_path('PREVIEW_ICONS', PREVIEW_ICONS)
content_dir.register_path(
    'ACTIVE_SPECIAL_CATEGORY_ICONS', ACTIVE_SPECIAL_CATEGORY_ICONS)
content_dir.register_path(
    'INACTIVE_SPECIAL_CATEGORY_ICONS', INACTIVE_SPECIAL_CATEGORY_ICONS)
content_dir.register_path('CHARACTER_DIR', CHARACTER_DIR)
content_dir.register_path('CHARACTER_OVERWORLD_DIR', CHARACTER_OVERWORLD_DIR)
content_dir.register_path('ITEM_DIR', ITEM_DIR)
content_dir.register_path('ITEM_OVERWORLD_DIR', ITEM_OVERWORLD_DIR)
content_dir.register_path('ENVIRONMENT_DIR', ENVIRONMENT_DIR)
