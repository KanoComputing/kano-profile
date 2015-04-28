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
                               ACTIVE_CATEGORY_ICONS, INACTIVE_CATEGORY_ICONS,
                               ACTIVE_SPECIAL_CATEGORY_ICONS,
                               INACTIVE_SPECIAL_CATEGORY_ICONS,
                               CIRC_ASSET_MASK, RING_ASSET, PREVIEW_ICONS,
                               ENVIRONMENT_DIR, AVATAR_SCRATCH,
                               AVATAR_DEFAULT_LOC, AVATAR_DEFAULT_NAME,
                               PLAIN_MASK)
from kano.logging import logger

from kano_profile.badges import calculate_badges
from kano_profile.profile import (set_avatar, set_environment,
                                  save_profile_variable)

# TODO Check which types of names are case sensitive


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
    _date_created = ''
    _item_id = ''
    _display_order = 0
    _is_unlocked = False

    _img = None

    def __init__(self, name, category, file_name, preview_img, x, y, date_created, item_id, is_unlocked, display_order):
        self._category = category
        self._name = name
        self._img_position_x = x
        self._img_position_y = y
        self._date_created = date_created
        self._item_id = item_id
        self._display_order = display_order
        self._is_unlocked = is_unlocked
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

    def is_unlocked(self):
        return self._is_unlocked

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
        # We need to remove the transparency of the item so that it doesn't
        # cause a gap on the base layer.
        r, g, b, a = self._img.split()
        item = Image.merge('RGB', (r, g, b))
        transp_mask = Image.merge("L", (a,))
        img.paste(item, position, transp_mask)

    def get_preview_img(self):
        """ Provides the item's preview image path
        :returns: absolute path to preview image as a string
        """
        return self._img_preview

    def get_id(self):
        """ Provides the unique id for the item
        :returns: unique id as a string
        """
        return self._item_id

    def get_date(self):
        """ Provides the creation date of the item
        :returns: creation date as a string
        """
        return self._date_created

    def get_disp_order(self):
        """ Provides the display order of the item
        :returns: display index as an integer
        """
        return self._display_order


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
    _display_order = 0
    _date_created = ''
    _character_id = ''
    _is_unlocked = False

    def __init__(self, name, file_name, preview_img, x, y, date_created, char_id, is_unlocked, display_order):
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
        self._display_order = display_order
        self._character_id = char_id
        self._date_created = date_created
        self._is_unlocked = is_unlocked

    def load_image(self):
        """ Loads the character's image internally. This is necessary before
        pasting the item over a character.
        """
        self._img = Image.open(self._asset_fname)

    def name(self):
        return self._name

    def get_img(self):
        """ Get the image class for the character.
        :returns: Image class (from PIL module)
        """
        return self._img

    def is_unlocked(self):
        return self._is_unlocked

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

    def generate_circular_assets(self, file_name_plain, file_name_ring):
        """ This function creates the circular assets that are required for the
        kano profile
        :param file_name: Path to where the completed file should be saved as a
                          string
        """
        rc_plain = self._generate_plain_circular(file_name_plain)

        # TODO remove the hardcoding of 54
        rc_ring = self._generate_white_circular(file_name_ring, resize=54)
        return rc_plain and rc_ring

    def _generate_white_circular(self, file_name, resize=0):
        return self._generate_ring_circular(file_name, RING_ASSET, CIRC_ASSET_MASK, resize=resize)

    def _generate_plain_circular(self, file_name):
        return self._generate_ring_circular(file_name, PLAIN_MASK, PLAIN_MASK, invert_order=True)

    def _generate_ring_circular(self, file_name, ring, mask, invert_order=False, resize=0):
        """ Creates the circular asset to be used in the top left corner on the
        desktop
        :param file_name: Path to where the completed (and resized if set so)
                          file will be saved as a string
        :param resize: (Optional) The size of the side of the resulting resized
                       image (Will be a square)
        """
        ring_img = Image.open(ring)
        mask_img = Image.open(mask)

        if ring_img.size != mask_img.size:
            logger.warn('Mask and ring asset do not have the same size')
            return False

        cropped_img = self._get_image_cropped(mask_img.size[0], mask_img.size[1])

        if not invert_order:
            img_out = Image.composite(ring_img, cropped_img, mask_img)
        else:
            img_out = Image.composite(cropped_img, ring_img, mask_img)

        # Resize to specified width if set
        if resize != 0:
            if img_out.size[0] != img_out.size[1]:
                logger.warn("Image is not square, resizing it will distort it")
            if resize < 0:
                logger.error(
                    "Resize value negative: {}, won't continue".format(resize)
                )
                return False
            img_out.thumbnail((resize, resize), Image.ANTIALIAS)

        img_out.save(file_name)
        logger.debug("created {}".format(file_name))
        return True

    def _get_image_cropped(self, size_x, size_y):
        """ Get an instance of the base image centred at the coordinates held
        by the internal variables and cropped to an exact size
        :param size_x: Size of the final image in the x dimension
        :param size_y: Size of the final image in the y dimension
        :returns: Instance of PIL Image
        """
        # Create a box of useful image data
        x_left = int(size_x / 2)
        x_right = size_x - x_left

        y_up = int(size_y / 2)
        y_down = size_y - y_up

        box = (self._crop_x - x_left,
               self._crop_y - y_up,
               self._crop_x + x_right,
               self._crop_y + y_down)

        return self._img.crop(box)

    def get_preview_img(self):
        """ Provides the Character's preview image path
        :returns: absolute path to preview image as a string
        """
        return self._img_preview

    def get_id(self):
        """ Provides the unique id for the character
        :returns: unique id as a string
        """
        return self._character_id

    def get_date(self):
        """ Provides the creation date of the character
        :returns: creation date as a string
        """
        return self._date_created

    def get_disp_order(self):
        """ Provides the display order of the character
        :returns: display index as an integer
        """
        return self._display_order


class AvatarEnvironment():
    """ Class for handling the environment (background) for a character. As
    it contains the image that will work as the background (lowest z-index)
    but also the largest in terms of size, it deserves a class of its own.
    """
    _name = ''
    _asset_fname = ''
    _img_preview = ''
    _img = None
    _date_created = ''
    _environment_id = ''
    _display_order = 0
    _is_unlocked = False

    def __init__(self, name, file_name, preview_img, date_created, env_id, is_unlocked, display_order):
        self._name = name
        self._date_created = date_created
        self._display_order = display_order
        self._environment_id = env_id
        self._is_unlocked = is_unlocked
        if os.path.isabs(file_name):
            self._asset_fname = file_name
        else:
            self._asset_fname = os.path.join(ENVIRONMENT_DIR, file_name)

        if os.path.isabs(preview_img):
            self._img_preview = preview_img
        else:
            self._img_preview = os.path.join(PREVIEW_ICONS, preview_img)

    def name(self):
        """ Provides the display name of the Item
        :returns: display name of character as a string
        """
        return self._name

    def get_preview_img(self):
        """ Provides the Background preview image path
        :returns: absolute path to preview image as a string
        """
        return self._img_preview

    def is_unlocked(self):
        return self._is_unlocked

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
            err_msg = "Image to be attached to the environment doesn't is None, will exit"
            logger.warn(err_msg)
            return False

        if x < 0 or x >= 1:
            err_msg = 'Argument x given to attach_char is out of bounds [0,1)'
            logger.error(err_msg)
            return False
        if y < 0 or y >= 1:
            err_msg = 'Argument x given to attach_char is out of bounds [0,1)'
            logger.error(err_msg)
            return False

        if not self._img:
            err_msg = "Internal envir Image hasn't been loaded. Will load now"
            logger.debug(err_msg)
            self.load_image()

        # Resize avatar if we can't fit it in (Normally shouldn't happen
        # but it makes testing without properly sized assets easier)
        char_szx = char_img.size[0]
        char_szy = char_img.size[1]

        if char_szx > self.get_img().size[0] or \
           char_szy > self.get_img().size[1]:
            # First calculate the reduction coefficient
            # so that no side is larger than 90% of the background canvas
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
        :returns: Always True (for now, wink wink)
        """
        # TODO Error checking
        self._img.save(file_name)
        return True

    def get_id(self):
        """ Provides the unique id for the environment
        :returns: unique id as a string
        """
        return self._environment_id

    def get_date(self):
        """ Provides the creation date of the environment
        :returns: creation date as a string
        """
        return self._date_created

    def get_disp_order(self):
        """ Provides the display order of the environment
        :returns: display index as an integer
        """
        return self._display_order


class AvatarConfParser():
    """ A class to take on the important task of parsing the configuration
    file used for generating new Avatars.
    Please use this class only if you require only parsing of the
    conf file, otherwise please use the AvatarCreator() class
    """
    _categories = set()
    _zindex = set()
    _cat_to_z_index = {}
    _cat_to_disp_order = {}
    _zindex_to_categories = {}
    _objects = {}
    _characters = {}
    _environments = {}
    _object_per_cat = {}
    _inactive_category_icons = {}
    _active_category_icons = {}
    _selected_borders = {}
    _hover_borders = {}
    _inactive_special_category_icons = {}
    _active_special_category_icons = {}
    _border_special_cat = {}
    _hover_border_special_cat = {}
    categories_label = 'categories'
    objects_label = 'objects'
    char_label = 'characters'
    env_label = 'environments'
    spec_cat_label = 'special_categories'
    special_category_labels = [char_label, env_label]
    _special_cat_to_disp_order = {}

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

        self._populate_environment_structures(conf_data)

        if self.spec_cat_label not in conf_data:
            logger.error('{} dict not found'.format(self.spec_cat_label))
        else:
            self._populate_special_category_structures(conf_data)

    def _populate_cat_structures(self, categories):
        """ Populates internal structures related to categories
        :param categories: categories section of YAML format configuration
                           structure read from file
        """
        for cat in categories:
            self._cat_to_z_index[cat['cat_name']] = cat['z_index']
            icon_file = cat['disp_icon']
            # TODO Fix the following if the icon_file is absolute
            if not os.path.isabs(icon_file):
                active_icon_file = os.path.join(ACTIVE_CATEGORY_ICONS,
                                                icon_file)
                inactive_icon_file = os.path.join(INACTIVE_CATEGORY_ICONS,
                                                  icon_file)
            self._active_category_icons[cat['cat_name']] = active_icon_file
            self._inactive_category_icons[cat['cat_name']] = inactive_icon_file

            selected_border_file = os.path.join(PREVIEW_ICONS,
                                                cat['selected_border'])
            self._selected_borders[cat['cat_name']] = selected_border_file
            hover_border_file = os.path.join(PREVIEW_ICONS,
                                             cat['hover_border'])
            self._hover_borders[cat['cat_name']] = hover_border_file
            self._cat_to_disp_order[cat['cat_name']] = cat['display_order']

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
            new_disp_ord = obj['display_order']
            new_date = obj['date_created']
            new_id = obj['item_id']
            # TODO hardcoded True for now
            new_unlock = True
            new_obj = AvatarAccessory(new_name,
                                      new_cat,
                                      new_fname,
                                      new_prev_img,
                                      new_x,
                                      new_y,
                                      new_date,
                                      new_id,
                                      new_unlock,
                                      new_disp_ord)
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
            new_disp_ord = obj['display_order']
            new_date = obj['date_created']
            new_id = obj['character_id']
            # TODO This is hardcoded for now
            new_unlock = True
            new_obj = AvatarCharacter(new_name,
                                      new_fname,
                                      new_prev_img,
                                      x,
                                      y,
                                      new_date,
                                      new_id,
                                      new_unlock,
                                      new_disp_ord)
            self._characters[new_name] = new_obj

    def _populate_environment_structures(self, conf_data):
        """ Populates internal structures related to environments (backgrounds)
        :param conf_data: YAML format configuration structure read from file
        """
        envirs = calculate_badges()

        for _, env in envirs[self.env_label]['all'].iteritems():
            new_name = env['title']
            new_fname = env['img_name']
            new_id = env['item_id']
            new_disp_ord = env['display_order']
            new_date = env['date_created']
            new_unlocked = env['achieved']
            if new_unlocked:
                new_prev_img = env['preview_img']
            else:
                # TODO Unhardcode this
                new_prev_img = 'environments/locked.png'
            new_env = AvatarEnvironment(new_name,
                                        new_fname,
                                        new_prev_img,
                                        new_date,
                                        new_id,
                                        new_unlocked,
                                        new_disp_ord)
            self._environments[new_name] = new_env

    def _populate_special_category_structures(self, conf_data):
        """ Populate internal structures related to the special categories
        such as characters and environments
        :param conf_data: YAML format configuration structure read from file
        """
        special_cat_data = conf_data[self.spec_cat_label]

        for special_cat in self.special_category_labels:
            active_icon_file = special_cat_data[special_cat]['active_icon']
            if not os.path.isabs(active_icon_file):
                active_icon_file = os.path.join(ACTIVE_SPECIAL_CATEGORY_ICONS,
                                                active_icon_file)

            inactive_icon_file = special_cat_data[special_cat]['inactive_icon']
            if not os.path.isabs(inactive_icon_file):
                inactive_icon_file = os.path.join(
                    INACTIVE_SPECIAL_CATEGORY_ICONS,
                    inactive_icon_file)

            border_icon_file = special_cat_data[special_cat]['selected_border']
            if not os.path.isabs(border_icon_file):
                border_icon_file = os.path.join(PREVIEW_ICONS,
                                                border_icon_file)

            hover_icon_file = special_cat_data[special_cat]['hover_border']
            if not os.path.isabs(hover_icon_file):
                hover_icon_file = os.path.join(PREVIEW_ICONS,
                                               hover_icon_file)

            self._active_special_category_icons[special_cat] = active_icon_file
            self._inactive_special_category_icons[special_cat] = inactive_icon_file
            self._border_special_cat[special_cat] = border_icon_file
            self._hover_border_special_cat[special_cat] = hover_icon_file
            self._special_cat_to_disp_order[special_cat] = \
                special_cat_data[special_cat]['display_order']

    def get_zindex(self, category):
        if category not in self._cat_to_z_index:
            logger.warn('Category {} not in available ones'.format(category))
        else:
            return self._cat_to_z_index[category]

    def _get_reg_item_cat(self, item_name):
        if item_name in self._objects:
            return self._objects[item_name].category()
        else:
            return None

    def get_item_category(self, item_name):
        cat_label = self._get_reg_item_cat(item_name)
        if not cat_label:
            if item_name not in self._environments:
                logger.warn('Item {} neither in obj nor in env list'.format(item_name))
                return None
            else:
                cat_label = self.env_label
        return cat_label

    def list_available_chars(self):
        """ Provides a list of available characters
        :returns: list of characters (list of strings)
        """
        return [k for k in self._characters.keys()]

    def _list_all_available_regular_objs(self):
        """ Provides a list of available regular objects
        :returns: list of objects (list of strings)
        """
        return [k for k in self._objects.keys()]

    def list_all_available_environments(self):
        """ Provides a list of available environments
        :returns: list of environments (list of strings)
        """
        env_inst_ord = sorted(self._environments.itervalues(),
                              key=lambda env: env.get_disp_order())
        return [k.name() for k in env_inst_ord]

    def list_all_available_objs(self):
        """ Provides a list of available objects
        :returns: list of objects (list of strings)
        """
        ret = self._list_all_available_regular_objs()
        ret.extend(self.list_all_available_environments())
        return ret

    def _get_avail_objs_regular_cat(self, category):
        """ Provides a list of available objects for the specific normal category
        :returns: [] of object names
                  None if category is not found
        """
        if category not in self._object_per_cat:
            err_msg = "cat {} not found, can't return objects".format(category)
            logger.warn(err_msg)
            return None
        else:

            item_inst_sorted = sorted(self._object_per_cat[category],
                                      key=lambda obj: obj.get_disp_order())
            return [it.name() for it in item_inst_sorted]

    def get_avail_objs(self, category):
        """ Provides a list of available objects for the category provided
        :returns: [] of object names
                  None if category is not found
        """
        if category == self.env_label:
            return self.list_all_available_environments()
        else:
            return self._get_avail_objs_regular_cat(category)

    def _list_available_regular_categories(self):
        """ Provides a list of available regular categories (not case
        sensitive)
        :returns: list of categories (list of strings)
        """
        reg_cats_ord = sorted(self._cat_to_disp_order.iteritems(),
                              key=lambda k: k[1])
        return [k[0] for k in reg_cats_ord]

    def _list_available_special_categories(self):
        """ Provides a list of available special categories (not case
        sensitive)
        :returns: list of categories (list of strings)
        """
        # TODO Temporary hardcoding
        # return self.special_category_labels
        # At the time it is only one so it is sorted
        return [self.env_label]

    def list_available_categories(self):
        """ Provides a list of available categories (not case sensitive)
        :returns: list of categories (list of strings)
        """
        cats = self._list_available_regular_categories()
        specs = self._list_available_special_categories()

        cats.extend(specs)
        return cats

    def get_inactive_category_icon(self, category_name):
        """ Provides the filename of the inactive icons of the provided
        category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        return self._get_inactive_reg_category_icon(category_name) or \
            self._get_inactive_special_category_icon(category_name)

    def _get_inactive_reg_category_icon(self, category_name):
        """ Provides the filename of the active icons of the provided
        regular category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._inactive_category_icons:
            err_msg = "Cat {} not found, can't provide inactive icon path".format(category_name)
            logger.warn(err_msg)
            return None
        else:
            return self._inactive_category_icons[category_name]

    def get_active_category_icon(self, category_name):
        """ Provides the filename of the active icons of the provided category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        return self._get_active_reg_category_icon(category_name) or \
            self._get_active_special_category_icon(category_name)

    def _get_active_reg_category_icon(self, category_name):
        """ Provides the filename of the active icons of the provided active
        category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._active_category_icons:
            logger.warn("Cat {} not found, can't provide active icon path"
                        .format(category_name))
            return None
        else:
            return self._active_category_icons[category_name]

    def get_selected_border(self, category_name):
        """ Provides the filename of the selected border of the preview icon
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        return self._get_selected_border_regular(category_name) or \
            self._get_selected_border_special(category_name)

    def _get_selected_border_regular(self, category_name):
        """ Provides the filename of the selected border of the preview icon
        :param category_name: Regular category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._selected_borders:
            logger.warn("Cat {} was not found, can't provide selected border path".format(category_name))
            return None
        else:
            return self._selected_borders[category_name]

    def get_hover_border(self, category_name):
        """ Provides the filename of the hover over border of the preview icon
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        return self._get_hover_border_regular(category_name) or \
            self._get_hover_border_special(category_name)

    def _get_hover_border_regular(self, category_name):
        """ Provides the filename of the hover border of the preview icon
        :param category_name: Regular category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if category_name not in self._hover_borders:
            logger.warn("Cat {} was not found, can't provide hover border path".format(category_name))
            return None
        else:
            return self._hover_borders[category_name]

    def _get_inactive_special_category_icon(self, special_category_name):
        """ Provides the filename of the active icons of the provided category
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if special_category_name not in self._inactive_special_category_icons:
            logger.warn("Special Cat {} not found, can't provide inactive icon path".format(special_category_name))
            return None
        else:
            return self._inactive_special_category_icons[special_category_name]

    def _get_active_special_category_icon(self, special_category_name):
        """ Provides the filename of the inactive icons of the provided category
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if special_category_name not in self._active_special_category_icons:
            logger.warn("Special Cat {} not found, can't provide active icon path".format(special_category_name))
            return None
        else:
            return self._active_special_category_icons[special_category_name]

    def _get_selected_border_special(self, special_category_name):
        """ Provides the filename of the selected border of the preview icon
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        self._border_special_cat
        if special_category_name not in self._border_special_cat:
            logger.warn("Special Cat {} not found, can't provide selected border path".format(special_category_name))
            return None
        else:
            return self._border_special_cat[special_category_name]

    def _get_hover_border_special(self, special_category_name):
        """ Provides the filename of the hover border of the preview icon
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        """
        if special_category_name not in self._hover_border_special_cat:
            logger.warn("Special Cat {} not found, can't provide hover border path".format(special_category_name))
            return None
        else:
            return self._border_special_cat[special_category_name]

    def get_char_preview(self, char_name):
        """ Provides the preview image for a given character
        :param char_name: Character whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the character is not available
        """
        if char_name not in self._characters:
            logger.warn("Char {} not in avail char list, can't return preview img".format(char_name))
            return None
        else:
            return self._characters[char_name].get_preview_img()

    def get_item_preview(self, item_name):
        """ Provides the preview image for a given item
        :param item_name: item whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the item is not available
        """
        return self._get_reg_item_preview(item_name) or \
            self._get_environment_preview(item_name)

    def _get_reg_item_preview(self, item_name):
        """ Provides the preview image for a given regular item
        :param item_name: item whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the item is not available
        """
        if item_name not in self._objects:
            logger.warn("Item {} not in avail obj list, can't return preview img".format(item_name))
            return None
        else:
            return self._objects[item_name].get_preview_img()

    def _get_environment_preview(self, environment_name):
        """ Provides the preview image for a given environment
        :param environment_name: environment whose preview image will be
                                 returned
        :returns: The absolute path to the preview image as a str or
                  None if the environment is not available
        """
        if environment_name not in self._environments:
            err_msg = "Envir {} not in avail env list, can't return preview img".format(environment_name)
            logger.warn(err_msg)
            return None
        else:
            return self._environments[environment_name].get_preview_img()

    def is_unlocked(self, item_name):
        """ Returns whether the item/environment is locked
        :param item_name: item whose lock status will be returned
        :returns: True iff it is unlocked
        """
        return self._is_unlocked_reg_item(item_name) or self._is_unlocked_env(item_name)

    def _is_unlocked_reg_item(self, item_name):
        if item_name not in self._objects:
            logger.debug("Item {} not in avail obj list, can't return lock state".format(item_name))
            return None
        else:
            return self._objects[item_name].is_unlocked()

    def _is_unlocked_env(self, item_name):
        if item_name not in self._environments:
            logger.debug("Item {} not in avail env list, can't return lock state".format(item_name))
            return None
        else:
            return self._environments[item_name].is_unlocked()


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
        """ Set an environment for the background. If the environment given is
        not unlocked a different unlocked one is selected in random
        :param env_name: Environment name
        :returns: True iff the environment exists (is available)
        """
        if env_name in self._environments:
            if not self._environments[env_name].is_unlocked():
                warn_msg = "Environment {} is locked, replacing with random".format(env_name)
                logger.warn(warn_msg)
                # Select randomly among the unlocked environments
                self._sel_env = random.choice([env for env in self._environments.itervalues() if env.is_unlocked()])
            else:
                self._sel_env = self._environments[env_name]
            logger.debug('Selected Environment: {}'.format(self._sel_env.name()))
            return True
        else:
            error_msg = 'Environment {} is not in the available env list'.format(env_name)
            logger.error(error_msg)
            return False

    def clear_env(self):
        """ Clear the selection for the environment
        """
        self._sel_env = None

    def selected_char_asset(self):
        """ Get the asset path for the image corresponding to the
        characted that has been selected
        :returns: the image path as a string, None if no character has been
                  selected
        """
        if self._sel_char is None:
            logger.warn("Character not selected, can't return path to asset")
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
        """ Specify the items to be used for the character. if any of the
        items are locked, replace with a different unlocked one from the
        same category.
        :param obj_names: list of item names
        :returns: False if any of the objects doesn't exist or if there are
                  multiple items from the same category are selected.
        """
        if clear_existing:
            self.clear_sel_objs()
            self.clear_env()

        sel_env_flag = False

        for obj_name in obj_names:
            if obj_name in self._objects:
                # Deal with the object if it is a regular item
                obj_instance = self._objects[obj_name]
                # Check whether we have selected multiple items from the same category
                if obj_instance.category() in self._sel_obj_per_cat:
                    error_msg = 'Multiple objects in category {}'.format(obj_instance.category())
                    logger.error(error_msg)
                    return False
                # Check whether it is unlocked
                if not obj_instance.is_unlocked():
                    error_msg = 'Item {} is locked, replacing with random from category {}'.format(obj_name, obj_instance.category())
                    logger.warn(error_msg)
                    obj_instance = random.choice([obj for obj in self._object_per_cat[obj_instance.category()] if obj.is_unlocked()])

                obj_cat = obj_instance.category()
                self._sel_obj_per_cat[obj_cat] = obj_instance
                self._sel_obj[obj_instance.name()] = obj_instance

                # Create a dictionary with which objects belong to each z-index
                obj_zindex = self.get_zindex(obj_cat)
                if obj_zindex not in self._sel_objs_per_zindex:
                    self._sel_objs_per_zindex[obj_zindex] = []

                self._sel_objs_per_zindex[obj_zindex].append(obj_instance)
            elif obj_name in self._environments:
                # Deal with the object if it is an environment
                if not sel_env_flag:
                    self.env_select(obj_name)
                    sel_env_flag = True
                else:
                    msg = "Provided multiple environments to select {}, {}".format(self._sel_env.name(), obj_name)
                    logger.error(msg)
                    return False
            else:
                # if it is neither show error message
                error_msg = 'Object {} not in available obj or env list'.format(obj_name)
                logger.error(error_msg)
                return False
        return True

    def randomise_rest(self, obj_names, empty_cats=False):
        """ Add specified objects and randomise the remaining ones
        :param obj_names: list of item names
        :param empty_cats: (Optional) set to True if it is acceptable to get
                           categories without any objects.
        :returns: False if any of the objects doesn't exist or if there are
                  multiple items from the same category are selected.
        """
        random_item_names = []
        # Select ones we definitely want
        rc = self.obj_select(obj_names)
        if not rc:
            return False
        # For categories where we haven't specified, select randomly
        for cat in self._categories.difference(
                set(self._sel_obj_per_cat.keys())):
            # Need to make sure that we can handle categories that contain no
            # items
            try:
                available_objs = [obj for obj in self._object_per_cat[cat]
                                  if obj.is_unlocked()]
                if empty_cats:
                    available_objs.append(None)
                choice = random.choice(available_objs)
                if choice:
                    random_item_names.append(choice.name())
            except KeyError:
                log_msg = "Category {} doesn't contain any items".format(cat)
                logger.debug(log_msg)
                continue

        if not self._sel_env:
            available_envs = [env.name() for env in self._environments.itervalues() if env.is_unlocked()]
            choice_env = random.choice(available_envs)
            random_item_names.append(choice_env)

        rc = self.obj_select(random_item_names, clear_existing=False)

        if not rc:
            return False
        return True

    def randomise_all_items(self):
        """ Randomise all items for a character
        :returns: A list of the selected items
        """
        self.randomise_rest('')

        return self.selected_items_per_cat()

    def selected_items(self):
        """ Returns a list of the items that have been selected
        :returns: A list of the selected items
        """
        ret = self._sel_obj.keys()
        # if there is an env selected, append it to the list to be returned
        if self._sel_env:
            ret.append(self._sel_env.name())
        return ret

    def selected_items_per_cat(self):
        """ Returns a dictionary of the selected items organised by their
        category.
        :returns: A dict with [categ_labels] -> item_selected
        """
        return {cat: item.name() for cat, item in self._sel_obj_per_cat.iteritems()}

    def create_avatar(self, file_name=''):
        """ Create the finished main image and save it to file.
        :param file_name: (Optional) A filename to be used for the asset that
                          is generated
        :returns: None if there was an issue while creating avatar, the location
                  of the created file otherwise
        """
        ret = None
        rc = self._create_base_img()

        if not rc:
            logger.error("Can't create image")
            return None

        for zindex in sorted(self._sel_objs_per_zindex.keys()):
            items = self._sel_objs_per_zindex[zindex]
            for item in items:
                item.paste_over_image(self._sel_char.get_img())

        # write to specified location
        fname_actual = file_name[:]
        if not fname_actual:
            logger.info(
                "Haven't provided a filename to save asset,using default")

            fname_actual = AVATAR_SCRATCH
            if not os.path.isdir(os.path.dirname(fname_actual)):
                os.makedirs(os.path.dirname(fname_actual))

        if not self._sel_env:
            logger.error("Haven't selected environment, can't save character")
            return None
        else:
            # Save the final image with the background
            file_name_env = append_suffix_to_fname(fname_actual, '_inc_env')
            self.create_avatar_with_background(file_name_env)
            ret = file_name_env

        return ret

    def get_default_final_image_path(self):
        dn = os.path.join(
                os.path.abspath(os.path.expanduser(AVATAR_DEFAULT_LOC)),
                AVATAR_DEFAULT_NAME)
        return append_suffix_to_fname(dn, '_inc_env')

    def create_auxiliary_assets(self, file_name):
        """ Creates all of the auxiliary assets. This is to be used after the
        user has finalised his choices and we are about to synchronise with
        Kano World
        :param file_name: To be used as the base for generating the filenames of the other assets
        :returns: False iff the generation of any of the assets fails
        """
        # Avatar on its own
        rc = self.save_image(file_name)
        if not rc:
            logger.error("Couldn't save character, aborting auxiliary asset generation")
            return False

        # Circular assets
        fname_circ = append_suffix_to_fname(file_name, '_circ_ring')
        fname_plain = append_suffix_to_fname(file_name, '_circ_plain')
        rc_c = self.create_circular_assets(fname_plain, fname_circ)
        if not rc_c:
            logger.error("Couldn't create circular assets, aborting auxiliary asset generation")
            return False

        # Environment + avatar
        fname_env = append_suffix_to_fname(file_name, '_inc_env_page2')
        rc_env = self._sel_env.save_image(fname_env)
        if not rc_env:
            logger.error("Couldn't create environment asset, aborting auxiliary asset generation")
            return False
        # Shifted environment
        fname_env_23 = append_suffix_to_fname(file_name, '_inc_env_page2')
        rc_23 = self.create_avatar_with_background(fname_env_23,
                                                   x_offset=0.33,
                                                   reload_img=True)
        if not rc_23:
            logger.error("Couldn't create shifted environment asset, aborting auxiliary asset generation")
            return False

        return True

    def save_final_assets(self, dir_name, sync=True):
        """ Generates all types of assets and saves them to the directory and
        specified
        :param dir_name: The path to the base file, including the filename.
                         Other files are created from this filename and in
                         this directory (ex. '~/my_dir/my_new_char.png')
        :param sync: (Optional) Set to true to sync the avatar details with
                     the profile structure and if possible upload them to Kano
                     World
        :returns: True iff all operations necessary were successful
        """
        dn = os.path.abspath(os.path.expanduser(dir_name))

        direc = os.path.dirname(dn)
        # if the path to file does not exist, create it
        if not os.path.isdir(direc):
            os.makedirs(direc)

        rc = self.create_avatar(dn)
        if not rc:
            logger.error(
                'Encountered issue, stopping the creation of final assets'
            )
            return False

        logger.debug("Created {}".format(dn))
        rc = self.create_auxiliary_assets(dn)
        if not rc:
            logger.error("Encountered issue while creating aux assets")
            return False

        if sync:
            items_no_env = self.selected_items_per_cat()
            items_no_env.pop(self.env_label, None)
            # When saving a new character in the profile, ensure that
            # the right version is used to sync with the API
            save_profile_variable('version', 2)
            set_avatar(self._sel_char.name(), items_no_env)
            set_environment(self._sel_env.name(), sync=True)

        return True

    def create_avatar_with_background(self, file_name, x_offset=0.5, y_offset=0.5, reload_img=False):
        """ Generates and saves the final image together with the background
        :param file_name: name of the file to save the image to
        :param x_offset: offset (as a percentage) of the avatar on the x axis
        :param y_offset: offset (as a percentage) of the avatar on the y axis
        :param reload_img: Set to True to reset the image with the selected
                           background
        """
        if reload_img:
            self._sel_env.load_image()

        self._sel_env.attach_char(self._sel_char.get_img(),
                                  x=x_offset,
                                  y=y_offset)
        self._sel_env.save_image(file_name)
        logger.debug("created {}".format(file_name))

        return True

    def create_circular_assets(self, file_name_plain, file_name_ring):
        """ Save circular assets with the filename given
        :param file_name: filename to save the image to
        :returns: False if there was a problem, True otherwise
        """
        if not file_name_plain or not file_name_ring:
            logger.warn('No filenames given, will not save circular assets')
            return None

        if not self._sel_char:
            err_msg = "No character is selected, will not save circular assets"
            logger.error(err_msg)
            return None
        self._sel_char.generate_circular_assets(file_name_plain,
                                                file_name_ring)
        return True

    def _create_base_img(self):
        if self._sel_char is None:
            logger.error("You haven't specified a character")
            return False

        self._sel_char.load_image()
        self._sel_env.load_image()
        return True

    def save_image(self, file_name):
        """ Save image as a file
        :param file_name: Filename of the new file
        :returns: False if the a character hasn't been selected
                  True otherwise
        """
        if self._sel_char is None:
            logger.error("You haven't specified a character")
            return False

        self._sel_char.save_image(file_name)
        return True


# TODO Maybe transfer this to kano utils?
def append_suffix_to_fname(filename, suffix):
    """ Given a filename (that includes the extension) and a suffix, this
    function appends the suffix to the filename.
    Ex.
    'example.png', '_new' -> 'example_new.png'
    '/usr/local/share/foo.txt', '_old' -> '/usr/local/share/foo_old.txt'
    'foo', '_bar' -> 'foo_bar'
    :param filename: a string that contains a filename absolute, or relative,
                     with or without a an extension
    :param suffix: a string to be appended to the filename (before the
                   extension)
    :returns: The finalised string as file + suffix + extension
    """
    fname, exten = os.path.splitext(filename)
    return fname + suffix + exten


def get_avatar_conf():
    conf = None
    with open(AVATAR_CONF_FILE) as f:
        conf = yaml.load(f)

    if conf is None:
        logger.error('Conf file {} not found'.format(AVATAR_CONF_FILE))

    return conf
