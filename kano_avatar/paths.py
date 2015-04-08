#
# Path constants
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
import os

AVATAR_CONF_FILE = '/usr/share/kano-profile/rules/avatar_generator/conf.yaml'
AVATAR_ASSET_FOLDER = '/usr/share/kano-profile/media/images/avatar_generator'
CSS_PATH = '/usr/share/kano-profile/media/CSS/avatar_generator.css'

CHARACTER_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'characters')
ITEM_DIR = os.path.join(AVATAR_ASSET_FOLDER, 'items')

CATEGORY_ICONS = os.path.join(AVATAR_ASSET_FOLDER, 'categories')
ACTIVE_CATEGORY_ICONS = os.path.join(CATEGORY_ICONS, 'active')
INACTIVE_CATEGORY_ICONS = os.path.join(CATEGORY_ICONS, 'inactive')

PREVIEW_ICONS = os.path.join(AVATAR_ASSET_FOLDER, 'preview')
CIRC_ASSET_MASK = os.path.join(AVATAR_ASSET_FOLDER, 'helper_assets', 'circle_mask.png')
RING_ASSET = os.path.join(AVATAR_ASSET_FOLDER, 'helper_assets', 'grey_ring.png')
