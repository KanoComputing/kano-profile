#
# Logic for parsing and creating avatars for a Kano World profile
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
import os
import random
import yaml
from PIL import Image

from kano_avatar.paths import (AVATAR_CONF_FILE, CHARACTER_DIR, ITEM_DIR,
                               CATEGORY_ICONS, CIRC_ASSET_MASK, RING_ASSET)
from kano.logging import logger

# TODO Check which types of names are case sensitive


class AvatarAccessory():
    """ Class for handling items and applying them onto an Avatar Character
    class.
    """
    _category = ''
    _name = ''
    _asset_fname = ''
    _img_position_x = 0
    _img_position_y = 0

    _img = None

    def __init__(self, name, category, file_name, x, y):
        self._category = category
        self._name = name
        self._img_position_x = x
        self._img_position_y = y
        # if an absolute path is given use it instead, so that we can
        # override elements
        if os.path.isabs(file_name):
            self._asset_fname = file_name
        else:
            self._asset_fname = os.path.join(ITEM_DIR, file_name)

    def name(self):
        """ Provides the display name of the Item
        :returns: display name of character as a string
        """
        return self._name

    def category(self):
        """ Provides the category name to which the Item belongs to
        :returns: category name as a string
        """
        return self._category

    def get_fname(self):
        """ Provides the item's asset filename
        :returns: filename as a string
        """
        return self._asset_fname

    def load_image(self):
        """ Loads the asset's image internally. This is necessary before
        pasting the item over a character, however there is no need to call it
        externally.
        """
        self._img = Image.open(self.get_fname())

    def paste_over_image(self, img):
        """ Pastes the item's image over a character's base image. The
        position of where the image will be pasted is specified by the x,y
        coordinates given during the class' instantiation. (x,y are distances
        in pixels of the top left corner)
        :param img: Image class on which the pasting will occur
        """
        if self._img is None:
            self.load_image()
        # position of upper left corner
        position = (self._img_position_x, self._img_position_y)
        img.paste(self._img, position, self._img)


class AvatarCharacter():
    """ Class for handling an Avatar character. It holds the image data for
    the character so as to serve as a base on which the items are pasted on.
    """
    _name = ''
    _asset_fname = ''
    _img = None
    _crop_x = 0
    _crop_y = 0

    def __init__(self, name, file_name, x, y):
        self._name = name
        if os.path.isabs(file_name):
            self._asset_fname = file_name
        else:
            self._asset_fname = os.path.join(CHARACTER_DIR, file_name)
        self._crop_x = x
        self._crop_y = y

    def load_image(self):
        """ Loads the character's image internally. This is necessary before
        pasting the item over a character.
        """
        self._img = Image.open(self._asset_fname)

    def get_img(self):
        """ Get the image class for the character.
        :returns: Image class (from PIL module)
        """
        return self._img

    def get_fname(self):
        """ Provides the item's asset filename
        :returns: filename as a string
        """
        return self._asset_fname

    def save_image(self, file_name):
        """ Save character image (together with items that have been pasted on
        it), to a file.
        :param file_name: filename to be saved to as a string
        """
        self._img.save(file_name)

    def generate_circular_assets(self, file_name):
        """ This function creates the circular assets that are required for the
        kano profile
        :param file_name: Path to where the completed file should be saved as a
                          string
        """
        ring = Image.open(RING_ASSET)
        ring_mask = Image.open(CIRC_ASSET_MASK)

        if ring.size != ring_mask.size:
            logger.warn('Mask and ring asset do not have the same size')

        box = (self._crop_x,
               self._crop_y,
               self._crop_x + ring.size[0],
               self._crop_y + ring.size[1])

        cropped_img = self._img.crop(box)

        img_out = Image.composite(ring, cropped_img, ring_mask)

        img_out.save(file_name)


class AvatarConfParser():
    _categories = set()
    _levels = set()
    _cat_to_lvl = {}
    _level_to_categories = {}
    _objects = {}
    _characters = {}
    _object_per_cat = {}
    _category_icons = {}
    categories_label = 'categories'
    objects_label = 'objects'
    char_label = 'characters'

    def __init__(self, conf_data):
        if self.categories_label not in conf_data:
            logger.error('{} dict not found'.format(self.categories_label))
        else:
            self._populate_cat_structures(conf_data[self.categories_label])

        if self.char_label not in conf_data:
            logger.error('{} dict not found'.format(self.char_label))
        else:
            self._populate_character_structures(conf_data)

        if self.objects_label not in conf_data:
            logger.error('{} dict not found'.format(self.objects_label))
        else:
            self._populate_object_structures(conf_data)

    def _populate_cat_structures(self, categories):
        """ Populates internal structures related to categories
        :param categories: categories section of YAML format configuration
                           structure read from file
        """
        for cat in categories:
            self._cat_to_lvl[cat['cat_name']] = cat['level']
            icon_file = cat['disp_icon']
            if not os.path.isabs(icon_file):
                icon_file = os.path.join(CATEGORY_ICONS, icon_file)
            self._category_icons[cat['cat_name']] = icon_file

        # Save both the unique set of levels and categories
        self._categories = set(self._cat_to_lvl.keys())
        self._levels = set(self._cat_to_lvl.values())

        self._level_to_categories = {i: [] for i in self._levels}
        for cat_name, lvl in self._cat_to_lvl.items():
            self._level_to_categories[lvl].append(cat_name)

    def _populate_object_structures(self, conf_data):
        """ Populates internal structures related to items
        :param conf_data: YAML format configuration structure read from file
        """
        for obj in conf_data[self.objects_label]:
            new_name = obj['display_name']
            new_cat = obj['category']
            new_fname = obj['img_name']
            new_x = obj['position_x']
            new_y = obj['position_y']
            new_obj = AvatarAccessory(new_name,
                                      new_cat,
                                      new_fname,
                                      new_x,
                                      new_y)
            self._objects[new_name] = new_obj
            if new_cat not in self._object_per_cat:
                self._object_per_cat[new_cat] = []
            self._object_per_cat[new_cat].append(new_obj)

    def _populate_character_structures(self, conf_data):
        """ Populates internal structures related to characters
        :param conf_data: YAML format configuration structure read from file
        """
        for obj in conf_data[self.char_label]:
            new_name = obj['display_name']
            new_fname = obj['img_name']
            x = obj['crop_x']
            y = obj['crop_y']
            new_obj = AvatarCharacter(new_name, new_fname, x, y)
            self._characters[new_name] = new_obj

    def get_lvl(self, category):
        if category not in self._cat_to_lvl:
            logger.warn('Category {} not in available ones'.format(category))
        else:
            return self._cat_to_lvl[category]

    def list_available_chars(self):
        """ Provides a list of available characters
        :returns: list of characters (list of strings)
        """
        return [k for k in self._characters.keys()]

    def list_all_available_objs(self):
        """ Provides a list of available objects
        :returns: list of objects (list of strings)
        """
        return [k for k in self._objects.keys()]

    def get_avail_objs(self, category):
        """ Provides a list of available objects for the specific category
        :returns: [] of object names
                  None if category is not found
        """
        if category not in self._object_per_cat:
            logger.warn('cat {} not found, can\'t return objects'.format(category))
            return None
        else:
            return [it.name() for it in self._object_per_cat[category]]

    def list_available_categories(self):
        """ Provides a list of available categories (not case sensitive)
        :returns: list of categories (list of strings)
        """
        return [k for k in self._categories]

    def get_category_icon(self, category_name):
        """ Provides the filename of the icons of the provided category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._category_icons:
            logger.warn('Cat {} was not found, can\'t provide icon path'.format(category_name))
            return None
        else:
            return self._category_icons[category_name]


class AvatarCreator(AvatarConfParser):
    _sel_char = None
    _sel_obj = {}
    _sel_obj_per_cat = {}
    _sel_objs_per_lvl = {}

    def char_select(self, char_name):
        """ Set a character as a base
        :param char_name: Character name
        :returns: True iff the character exists (is available)
        """
        # Get the instance of the character
        if char_name in self._characters:
            self._sel_char = self._characters[char_name]
            return True
        else:
            error_msg = 'Character {} is not in the available char list'.format(char_name)
            logger.error(error_msg)
            return False

    def selected_char_asset(self):
        """ Get the asset path for the image corresponding to the
        characted that has been selected
        :returns: the image path as a string, None if no character has been
                  selected
        """
        if self._sel_char is None:
            logger.warn('Character not selected, can\'t return path to asset')
            return None
        else:
            return self._sel_char.get_fname()

    def clear_sel_objs(self):
        """ Clear structures that contain items that have been selected
        """
        self._sel_obj.clear()
        self._sel_obj_per_cat.clear()
        self._sel_objs_per_lvl.clear()

    def obj_select(self, obj_names, clear_existing=True):
        """ Specify the items to be used for the character.
        :param obj_names: list of item names
        :returns: False if any of the objects doesn't exist or if there multiplei
                  items from the same category are selected.
        """
        if clear_existing:
            self.clear_sel_objs()

        for obj_name in obj_names:
            if obj_name in self._objects:
                obj_instance = self._objects[obj_name]
                if obj_instance.category() in self._sel_obj_per_cat:
                    error_msg = 'Multiple objects in category {}'.format(obj_instance.category())
                    logger.error(error_msg)
                    return False

                obj_cat = obj_instance.category()
                self._sel_obj_per_cat[obj_cat] = obj_instance
                self._sel_obj[obj_name] = self._objects[obj_name]

                # Create a dictionary with which objects belong to each lvl
                obj_lvl = self.get_lvl(obj_cat)
                if obj_lvl not in self._sel_objs_per_lvl:
                    self._sel_objs_per_lvl[obj_lvl] = []

                self._sel_objs_per_lvl[obj_lvl].append(obj_instance)
            else:
                error_msg = 'Object {} not in available obj list'.format(obj_name)
                logger.error(error_msg)
                return False
        return True

    def randomise_rest(self, obj_names):
        """ Add specified objects and randomise the remaining ones
        :param obj_names: list of item names
        :returns: False if any of the objects doesn't exist or if there are
                  multiple items from the same category are selected.
        """
        random_item_names = []
        # Select ones we definitely want
        rc = self.obj_select(obj_names)
        if not rc:
            return False
        # For categories where we haven't specified, select randomly
        for cat in self._categories.difference(set(self._sel_obj_per_cat.keys())):
            available_objs = self._object_per_cat[cat][:]
            available_objs.append(None)
            choice = random.choice(available_objs)
            if choice:
                random_item_names.append(choice.name())

        rc = self.obj_select(random_item_names, clear_existing=False)

        if not rc:
            return False
        return True

    def randomise_all_items(self):
        """ Randomise all items for a character
        :returns: A list of the selected items
        """
        self.randomise_rest('')

        return self.selected_items()

    def selected_items(self):
        return self._sel_obj.keys()

    def create_avatar(self, save_to='', circ_assets=True):
        """ Create the finished image and (optionally) save it to file.
        :param save_to: (Optional) filename to save the image to
        :returns: False if the base character hasn't been specified
        """
        rc = self._create_base_img()

        if not rc:
            logger.error("Can't create image")
            return False

        for lvl in sorted(self._sel_objs_per_lvl.keys()):
            items = self._sel_objs_per_lvl[lvl]
            for item in items:
                item.paste_over_image(self._sel_char.get_img())

        # write to specified location
        if save_to:
            self.save_image(save_to)

            if circ_assets:
                file_name, file_ext = os.path.splitext(save_to)
                file_name += '_circ' + file_ext
                self._sel_char.generate_circular_assets(file_name)

        return True

    def _create_base_img(self):
        if self._sel_char is None:
            logger.error('You haven\'t specified a character')
            return False

        self._sel_char.load_image()
        return True

    def save_image(self, file_name):
        """ Save image as a file
        :param file_name: Filename of the new file
        :returns: False if the a character hasn't been selected
                  True otherwise
        """
        if self._sel_char is None:
            logger.error('You haven\'t specified a character')
            return False

        self._sel_char.save_image(file_name)
        return True


def get_avatar_conf():
    conf = None
    with open(AVATAR_CONF_FILE) as f:
        conf = yaml.load(f)

    if conf is None:
        logger.error('Conf file {} not found'.format(AVATAR_CONF_FILE))

    return conf
