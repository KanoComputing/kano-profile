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
                               CATEGORY_ICONS, CIRC_ASSET_MASK, RING_ASSET,
                               PREVIEW_ICONS, ENVIRONMENT_DIR)
from kano.logging import logger

# TODO Check which types of names are case sensitive
# TODO Add support to save multiple circular assets, currently only 1 is supported


class AvatarAccessory():
    """ Class for handling items and applying them onto an Avatar Character
    class.
    """
    _category = ''
    _name = ''
    _asset_fname = ''
    _img_preview = ''
    _img_position_x = 0
    _img_position_y = 0

    _img = None

    def __init__(self, name, category, file_name, preview_img, x, y):
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

        if os.path.isabs(preview_img):
            self._img_preview = preview_img
        else:
            self._img_preview = os.path.join(PREVIEW_ICONS, preview_img)

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

    def get_preview_img(self):
        """ Provides the item's preview image path
        :returns: absolute path to preview image as a string
        """
        return self._img_preview


class AvatarCharacter():
    """ Class for handling an Avatar character. It holds the image data for
    the character so as to serve as a base on which the items are pasted on.
    """
    _name = ''
    _asset_fname = ''
    _img_preview = ''
    _img = None
    _crop_x = 0
    _crop_y = 0

    def __init__(self, name, file_name, preview_img, x, y):
        self._name = name
        if os.path.isabs(file_name):
            self._asset_fname = file_name
        else:
            self._asset_fname = os.path.join(CHARACTER_DIR, file_name)

        if os.path.isabs(preview_img):
            self._img_preview = preview_img
        else:
            self._img_preview = os.path.join(CHARACTER_DIR, preview_img)
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

    def get_preview_img(self):
        """ Provides the Character's preview image path
        :returns: absolute path to preview image as a string
        """
        return self._img_preview


class AvatarEnvironment():
    """ Class for handling the environment (background) for a character. As
    it contains the image that will work as the background (lowest z-index)
    but also the largest in terms of size, it deserves a class of its own.
    """
    _name = ''
    _asset_fname = ''
    _img_preview = ''
    _img = None

    def __init__(self, name, file_name, preview_img):
        self._name = name
        if os.path.isabs(file_name):
            self._asset_fname = file_name
        else:
            self._asset_fname = os.path.join(ENVIRONMENT_DIR, file_name)

        if os.path.isabs(preview_img):
            self._img_preview = preview_img
        else:
            self._img_preview = os.path.join(PREVIEW_ICONS, preview_img)

    def get_preview_img(self):
        """ Provides the Background preview image path
        :returns: absolute path to preview image as a string
        """
        return self._img_preview

    def load_image(self):
        """ Loads the environment image internally.
        """
        self._img = Image.open(self._asset_fname).convert('RGBA')

    def attach_char(self, char_img, x=0.5, y=0.5):
        """ Attach a character to the environment. This method will overwrite
        the internal image to include the character with the environment in
        the background. In order to reset the environment you may use the
        .load_image() method
        :param char_img: Image object to be attached to the environment
        :param x: Value between [0,1) to control the position of the character
                  on the environment. It can be thought of like a percentage
                  of the total x axis of the image where the centre of the new
                  image will be pasted
        :param y: Value between [0,1) to control the position of the character
                  on the environment. It can be thought of like a percentage
                  of the total y axis of the image where the centre of the new
                  image will be pasted
        :returns: False if the operation is not successful (with appropriate
                  logging)
        """

        if not char_img:
            logger.warn('Image to be attached to the environment doesn\'t is None, will exit')
            return False

        if x < 0 or x >= 1:
            logger.error('Argument x given to attach_char is out of bounds [0,1)')
            return False
        if y < 0 or y >= 1:
            logger.error('Argument x given to attach_char is out of bounds [0,1)')
            return False

        if not self._img:
            logger.debug('Internal environment Image hasn\'t been loaded will load now')
            self.load_image()

        # Resize avatar if we can't fit it in (Normally shouldn't happen
        # but it makes testing without properly sized assets easier)
        char_szx = char_img.size[0]
        char_szy = char_img.size[1]

        if char_szx > self.get_img().size[0] or char_szy > self.get_img().size[1]:
            # First calculate the reduction coefficient
            # so that no side is larger than 80% of the background canvas
            coeff = 0.9
            c_x = coeff * self.get_img().size[0] / char_szx
            c_y = coeff * self.get_img().size[1] / char_szy
            c = min(c_x, c_y)
            new_size = (int(c * char_szx), int(c * char_szy))
            resized_char = char_img.resize(new_size, Image.ANTIALIAS)
        else:
            resized_char = char_img

        top_left_x = int(self.get_img().size[0] * x - resized_char.size[0]/2)
        top_left_y = int(self.get_img().size[1] * y - resized_char.size[1]/2)

        # We need to create a temporary image to hold the avatar since
        # in order to composite images they need to have the same size
        temp_img = Image.new(self.get_img().mode, self.get_img().size)
        temp_img.paste(resized_char, (top_left_x, top_left_y))

        self._img = Image.composite(temp_img, self.get_img(), temp_img)

        return True

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


class AvatarConfParser():
    """ A class to take on the important task of parsing the configuration
    file used for generating new Avatars.
    Please use this class only if you require only parsing of the
    conf file, otherwise please use the AvatarCreator() class
    """
    _categories = set()
    _zindex = set()
    _cat_to_z_index = {}
    _zindex_to_categories = {}
    _objects = {}
    _characters = {}
    _environments = {}
    _object_per_cat = {}
    _inactive_category_icons = {}
    _active_category_icons = {}
    _selected_borders = {}
    categories_label = 'categories'
    objects_label = 'objects'
    char_label = 'characters'
    env_label = 'environments'

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

        if self.env_label not in conf_data:
            logger.error('{} dict not found'.format(self.env_label))
        else:
            self._populate_environment_structures(conf_data)

    def _populate_cat_structures(self, categories):
        """ Populates internal structures related to categories
        :param categories: categories section of YAML format configuration
                           structure read from file
        """
        for cat in categories:
            self._cat_to_z_index[cat['cat_name']] = cat['z_index']
            icon_file = cat['disp_icon']
            if not os.path.isabs(icon_file):
                active_icon_file = os.path.join(CATEGORY_ICONS, 'active', icon_file)
                inactive_icon_file = os.path.join(CATEGORY_ICONS, 'inactive', icon_file)
            self._active_category_icons[cat['cat_name']] = active_icon_file
            self._inactive_category_icons[cat['cat_name']] = inactive_icon_file

            selected_border_file = os.path.join(PREVIEW_ICONS, cat['selected_border'])
            self._selected_borders[cat['cat_name']] = selected_border_file

        # Save both the unique set of z-indexes and categories
        self._categories = set(self._cat_to_z_index.keys())
        self._zindex = set(self._cat_to_z_index.values())

        self._zindex_to_categories = {i: [] for i in self._zindex}
        for cat_name, zindex in self._cat_to_z_index.items():
            self._zindex_to_categories[zindex].append(cat_name)

    def _populate_object_structures(self, conf_data):
        """ Populates internal structures related to items
        :param conf_data: YAML format configuration structure read from file
        """
        for obj in conf_data[self.objects_label]:
            new_name = obj['display_name']
            new_cat = obj['category']
            new_fname = obj['img_name']
            new_prev_img = obj['preview_img']
            new_x = obj['position_x']
            new_y = obj['position_y']
            new_obj = AvatarAccessory(new_name,
                                      new_cat,
                                      new_fname,
                                      new_prev_img,
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
            new_prev_img = obj['preview_img']
            x = obj['crop_x']
            y = obj['crop_y']
            new_obj = AvatarCharacter(new_name, new_fname, new_prev_img, x, y)
            self._characters[new_name] = new_obj

    def _populate_environment_structures(self, conf_data):
        """ Populates internal structures related to environments (backgrounds)
        :param conf_data: YAML format configuration structure read from file
        """
        for env in conf_data[self.env_label]:
            new_name = env['display_name']
            new_fname = env['img_name']
            new_prev_img = env['preview_img']
            new_env = AvatarEnvironment(new_name, new_fname, new_prev_img)
            self._environments[new_name] = new_env

    def get_zindex(self, category):
        if category not in self._cat_to_z_index:
            logger.warn('Category {} not in available ones'.format(category))
        else:
            return self._cat_to_z_index[category]

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

    def list_all_available_environments(self):
        """ Provides a list of available environments
        :returns: list of environments (list of strings)
        """
        return [k for k in self._environments.keys()]

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

    def get_inactive_category_icon(self, category_name):
        """ Provides the filename of the active icons of the provided category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._inactive_category_icons:
            logger.warn('Cat {} was not found, can\'t provide inactive '
                        'icon path'.format(category_name))
            return None
        else:
            return self._inactive_category_icons[category_name]

    def get_active_category_icon(self, category_name):
        """ Provides the filename of the inactive icons of the provided category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._active_category_icons:
            logger.warn('Cat {} was not found, can\'t provide active icon '
                        'path'.format(category_name))
            return None
        else:
            return self._active_category_icons[category_name]

    def get_selected_border(self, category_name):
        """ Provides the filename of the selected border of the preview icon
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._selected_borders:
            logger.warn('Cat {} was not found, can\'t provide selected border '
                        'path'.format(category_name))
            return None
        else:
            return self._selected_borders[category_name]

    def get_char_preview(self, char_name):
        """ Provides the preview image for a given character
        :param char_name: Character whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the character is not available
        """
        if char_name not in self._characters:
            logger.warn('Char {} not in avail char list, can\'t return preview img'.format(char_name))
            return None
        else:
            return self._characters[char_name].get_preview_img()

    def get_item_preview(self, item_name):
        """ Provides the preview image for a given item
        :param item_name: item whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the item is not available
        """
        if item_name not in self._objects:
            logger.warn('Item {} not in avail obj list, can\'t return preview img'.format(item_name))
            return None
        else:
            return self._objects[item_name].get_preview_img()

    def get_environment_preview(self, environment_name):
        """ Provides the preview image for a given environment
        :param environment_name: environment whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the environment is not available
        """
        if environment_name not in self._environments:
            logger.warn('Environment {} not in avail env list, can\'t return preview img'.format(environment_name))
            return None
        else:
            return self._environments[environment_name].get_preview_img()


class AvatarCreator(AvatarConfParser):
    """ The aim of this class is to help generate avatars for the kano world
    profile. It includes many accessor methods to get the attributes so that
    you don't have to use the internal structures.
    It has been designed and may be used from a GUI or a CLI
    Please note that when referring to items or characters, you may use their
    display name. However matching names to class objects is case sensitive.
    """
    _sel_char = None
    _sel_obj = {}
    _sel_obj_per_cat = {}
    _sel_objs_per_zindex = {}
    _sel_env = None

    def __init__(self, conf_data):
        AvatarConfParser.__init__(self, conf_data)

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

    def env_select(self, env_name):
        """ Set an environment for the background
        :param env_name: Environment name
        :returns: True iff the environment exists (is available)
        """
        if env_name in self._environments:
            self._sel_env = self._environments[env_name]
            return True
        else:
            error_msg = 'Environment {} is not in the available env list'.format(env_name)
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
        self._sel_objs_per_zindex.clear()

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

                # Create a dictionary with which objects belong to each z-index
                obj_zindex = self.get_zindex(obj_cat)
                if obj_zindex not in self._sel_objs_per_zindex:
                    self._sel_objs_per_zindex[obj_zindex] = []

                self._sel_objs_per_zindex[obj_zindex].append(obj_instance)
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
            # Need to make sure that we can handle categories that contain no
            # items
            try:
                available_objs = self._object_per_cat[cat][:]
                available_objs.append(None)
                choice = random.choice(available_objs)
                if choice:
                    random_item_names.append(choice.name())
            except KeyError:
                logger.debug('Category {} doesn\'t contain any items'.format(cat))
                continue

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

    def create_avatar(self, save_to='', circ_assets=True, save_background=True):
        """ Create the finished image and (optionally) save it to file.
        :param save_to: (Optional) filename to save the image to
        :param circ_assets: (Optional) If set the circular assets are with a
                            file_name same at the one set in the save_to
                            parameter with '_circ' appended
        :param save_background: (Optional) If set the the avatar together with
                                the background will be saved to a file_name
                                with '_inc_env' appended
        :returns: False if the base character hasn't been specified
        """
        rc = self._create_base_img()

        if not rc:
            logger.error("Can't create image")
            return False

        for zindex in sorted(self._sel_objs_per_zindex.keys()):
            items = self._sel_objs_per_zindex[zindex]
            for item in items:
                item.paste_over_image(self._sel_char.get_img())

        # write to specified location
        if save_to:
            self.save_image(save_to)

            if circ_assets:
                file_name, file_ext = os.path.splitext(save_to)
                file_name += '_circ' + file_ext
                self._sel_char.generate_circular_assets(file_name)

            if save_background:
                # If no environment has been selected, do nothing
                if self._sel_env:
                    file_name, file_ext = os.path.splitext(save_to)
                    file_name += '_inc_env' + file_ext
                    self._sel_env.attach_char(self._sel_char.get_img())
                    self._sel_env.save_image(file_name)

        return True

    def create_circular_assets(self, file_name):
        """ Save circular assets with the filename given
        :param file_name: filename to save the image to
        :returns: False if there was a problem, True otherwise
        """
        if not file_name:
            logger.warn('No filename given, will not save circular assets')
            return None

        if not self._sel_char:
            logger.error('Haven\'t selected a character, will not save circulat assets')
            return None
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
