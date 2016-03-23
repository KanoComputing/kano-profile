# character_components.py
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Character, item and other avatar related classes for a Kano World profile
from PIL import Image

from kano_avatar.paths import CIRC_ASSET_MASK, RING_ASSET, PLAIN_MASK
from kano.logging import logger
from kano_content.extended_paths import content_dir


class AvatarBase(object):
    """ Base class containing attributes and common methods to be used in
    classes that describe objects and categories of the profile avatar
    """
    def __init__(self, name='', unique_id='', disp_order=0, date_created=''):
        self._name = name
        self._unique_id = unique_id
        self._display_order = disp_order
        self._date_created = date_created

    def name(self):
        """ Provides the display name of the accessory
        :returns: display name of accessory as a string
        :rtype: string
        """
        return self._name

    def get_id(self):
        """ Provides the unique id for the accessory
        :returns: unique id as a string
        :rtype: string
        """
        return self._unique_id

    def get_disp_order(self):
        """ Provides the display order of the accessory
        :returns: display index as an integer
        :rtype: integer
        """
        return self._display_order

    def get_date(self):
        """ Provides the creation date of the accessory
        :returns: creation date as a string
        :rtype: string
        """
        return self._date_created


class AvatarBaseAccessory(AvatarBase):
    """ Base class containing attributes and common methods to be used in
    classes that describe objects that are related to the profile avatar
    """

    def __init__(self, asset_fname='', img_prev='', unlocked='', **kw):
        super(AvatarBaseAccessory, self).__init__(**kw)
        self._asset_fname = asset_fname
        self._img_preview = img_prev
        self._is_unlocked = unlocked
        self._img = None
        self._category = None

    def is_unlocked(self):
        """ Returns the locked state of the accessory
        :returns: lock state
        :rtype: Boolean
        """
        return self._is_unlocked

    def get_preview_img(self):
        """ Provides the accessory preview image path
        :returns: absolute path to preview image as a string
        :rtype: string
        """
        return self._img_preview

    def get_fname(self):
        """ Provides the accessory's asset filename
        :returns: filename as a string
        :rtype: string
        """
        return self._asset_fname

    def get_fname_overworld(self):
        """ Provides the accessory's asset filename for overworld
        :returns: filename as a string
        :rtype: string
        """
        return self._asset_fname_overworld

    def get_img(self):
        """ Get the image instance for the accessory.
        :returns: Image instance (from PIL module)
        :rtype: Image class (from PIL module)
        """
        return self._img

    def get_img_overworld(self):
        """ Get the image instance for the accessory for overworld.
        :returns: Image instance (from PIL module)
        :rtype: Image class (from PIL module)
        """
        return self._img_overworld

    def set_category(self, cat_obj):
        if not self._category:
            self._category = cat_obj
        else:
            logger.error("Item '{}' already points to a category {}".format(
                self, self._category))

    def category(self):
        """ Provides the category name to which the Item belongs to
        :returns: category name as a string
        :rtype: string
        """
        return self._category


class AvatarAccessory(AvatarBaseAccessory):
    """ Class for handling items and applying them onto an Avatar Character
    class.
    """

    @staticmethod
    def from_data(data):
        inst = None
        new_name = data['display_name']
        cat = data['category']
        char = data['character']
        new_fname = data['img_name']
        new_prev_img = data['preview_img']
        new_x = data['position_x']
        new_y = data['position_y']
        new_disp_ord = data['display_order']
        new_date = data['date_created']
        new_id = data['item_id']
        # TODO hardcoded all unlocked for items until we change them to
        # use the same scheme as environments
        new_unlock = True
        inst = AvatarAccessory(new_name,
                               new_fname,
                               new_prev_img,
                               new_x,
                               new_y,
                               new_date,
                               new_id,
                               new_unlock,
                               new_disp_ord)
        return inst, char, cat

    def __init__(self, name, file_name, preview_img, x, y,
                 date_created, item_id, is_unlocked, display_order):
        super(AvatarAccessory, self).__init__(
            name=name, unique_id=item_id, disp_order=display_order,
            date_created=date_created, unlocked=is_unlocked)
        self._img_position_x = x
        self._img_position_y = y
        # if an absolute path is given use it instead, so that we can
        # override elements
        self._asset_fname = content_dir.get_file('ITEM_DIR', file_name)
        self._asset_fname_overworld = content_dir.get_file('ITEM_OVERWORLD_DIR', file_name)
        self._img_preview = content_dir.get_file('PREVIEW_ICONS', preview_img)

    def __repr__(self):
        return 'Item {} of category {}'.format(self.get_id(), self.category())

    def load_image(self):
        """ Loads the asset's image internally. This is necessary before
        pasting the item over a character, however there is no need to call it
        externally.
        """
        self._img = Image.open(self.get_fname())
        self._img_overworld = Image.open(self.get_fname_overworld())

    def paste_over_image(self, img, img_overworld):
        """ Pastes the item's image over a character's base image. The
        position of where the image will be pasted is specified by the x,y
        coordinates given during the class' instantiation. (x,y are distances
        in pixels of the top left corner)
        :param img: PIL Image class on which the pasting will occur
        """
        if self.get_img() is None or self.get_img_overworld() is None:
            self.load_image()
        # position of upper left corner
        position = (self._img_position_x, self._img_position_y)
        # We need to remove the transparency of the item so that it doesn't
        # cause a gap on the base layer.
        r, g, b, a = self._img.split()
        item = Image.merge('RGB', (r, g, b))
        transp_mask = Image.merge("L", (a,))
        img.paste(item, position, transp_mask)

        # repeat for overworld image, but no offset

        r, g, b, a = self._img_overworld.split()
        item = Image.merge('RGB', (r, g, b))
        transp_mask = Image.merge("L", (a,))
        img_overworld.paste(item, (0, 0), transp_mask)


class AvatarCharacter(AvatarBaseAccessory):
    """ Class for handling an Avatar character. It holds the image data for
    the character so as to serve as a base on which the items are pasted on.
    """
    @staticmethod
    def from_data(data):
        inst = None

        new_name = data['display_name']
        new_fname = data['img_name']
        new_prev_img = data['preview_img']
        x = data['crop_x']
        y = data['crop_y']
        new_disp_ord = data['display_order']
        new_date = data['date_created']
        new_id = data['character_id']
        # TODO hardcoded all unlocked for characters until we change them
        # to use the same scheme as environments
        new_unlock = True
        inst = AvatarCharacter(new_name,
                               new_fname,
                               new_prev_img,
                               x,
                               y,
                               new_date,
                               new_id,
                               new_unlock,
                               new_disp_ord)
        return inst

    def __init__(self, name, file_name, preview_img, x, y, date_created,
                 char_id, is_unlocked, display_order):
        super(AvatarCharacter, self).__init__(
            name=name, unique_id=char_id, disp_order=display_order,
            date_created=date_created, unlocked=is_unlocked)

        self._asset_fname = content_dir.get_file('CHARACTER_DIR', file_name)
        self._asset_fname_overworld = content_dir.get_file('CHARACTER_OVERWORLD_DIR', file_name)
        self._img_preview = content_dir.get_file('PREVIEW_ICONS', preview_img)

        self._crop_x = x
        self._crop_y = y

    def __repr__(self):
        return 'Character {}'.format(self.get_id())

    def load_image(self):
        """ Loads the character's image internally. This is necessary before
        pasting the item over a character.
        """
        self._img = Image.open(self.get_fname())
        self._img_overworld = Image.open(self.get_fname_overworld())

    def save_image(self, file_name):
        """ Save character image (together with items that have been pasted on
        it), to a file.
        :param file_name: filename to be saved to as a string
        """
        self._img.save(file_name)

    def save_image_overworld(self, file_name):
        """ Save character image (together with items that have been pasted on
        it), to a file.
        :param file_name: filename to be saved to as a string
        """
        self._img_overworld.save(file_name)

    def generate_circular_assets(self, file_name_plain, file_name_ring):
        """ This function creates the circular assets that are required for the
        kano profile
        :param file_name: Path to where the completed file should be saved as a
                          string
        """
        rc_plain = self._generate_plain_circular(file_name_plain)

        # 54 is the size of the stamp icon we require
        rc_ring = self._generate_white_circular(file_name_ring, resize=54)
        return rc_plain and rc_ring

    def _generate_white_circular(self, file_name, resize=0):
        return self._generate_ring_circular(
            file_name, RING_ASSET, CIRC_ASSET_MASK, resize=resize)

    def _generate_plain_circular(self, file_name):
        return self._generate_ring_circular(
            file_name, PLAIN_MASK, PLAIN_MASK, invert_order=True)

    def _generate_ring_circular(self, file_name, ring, mask,
                                invert_order=False, resize=0):
        """ Creates the circular asset to be used in the top left corner on the
        desktop. The mask and ring assets need to have the same size.
        :param file_name: Path to where the completed (and resized if set so)
                          file will be saved as a string
        :param ring: Path to the ring asset to be used
        :param mask: Path to the mast asset to be used
        :param invert_order: invert order of the ring and mask assets in the
                             composite function
        :type invert_order: Boolean
        :param resize: (Optional) The size of the side of the resulting resized
                       image (Will be a square)
        :type resize: integer
        :returns: True iff no errors have occurred
        :rtype: Boolean
        """
        ring_img = Image.open(ring)
        mask_img = Image.open(mask)

        if ring_img.size != mask_img.size:
            logger.warn('Mask and ring asset do not have the same size')
            return False

        cropped_img = self._get_image_cropped(
            mask_img.size[0], mask_img.size[1])

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
        """ Returns an instance of an image cropped to the specified
        dimensions, centered at the coordinates detailed by the class
        variables _crop_x and _crop_y.
        :param size_x: Size of the final image in the x dimension
        :param size_y: Size of the final image in the y dimension
        :returns: Instance of PIL Image
        :rtype: Image class from PIL module
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


class AvatarEnvironment(AvatarBaseAccessory):
    """ Class for handling the environment (background) for a character. As
    it contains the image that will work as the background (lowest z-index)
    but also the largest in terms of size, it deserves a class of its own.
    """
    @staticmethod
    def from_data(data):
        inst = None
        new_name = data['title']
        new_fname = data['img_name']
        new_id = data['item_id']
        new_disp_ord = data['display_order']
        new_date = data['date_created']
        new_unlocked = data['achieved']
        if new_unlocked:
            new_prev_img = data['preview_img']
        else:
            # TODO Unhardcode this
            new_prev_img = 'environments/locked.png'
        inst = AvatarEnvironment(new_name,
                                 new_fname,
                                 new_prev_img,
                                 new_date,
                                 new_id,
                                 new_unlocked,
                                 new_disp_ord)
        return inst

    def __init__(self, name, file_name, preview_img, date_created, env_id,
                 is_unlocked, display_order):
        super(AvatarEnvironment, self).__init__()
        self._name = name
        self._date_created = date_created
        self._display_order = display_order
        self._unique_id = env_id
        self._is_unlocked = is_unlocked

        self._asset_fname = content_dir.get_file('ENVIRONMENT_DIR', file_name)
        self._img_preview = content_dir.get_file('PREVIEW_ICONS', preview_img)

    def __repr__(self):
        return 'Environment {}'.format(self.get_id())

    def load_image(self):
        """ Loads the environment image internally.
        """
        self._img = Image.open(self.get_fname()).convert('RGBA')

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
        :rtype: Boolean
        """

        if not char_img:
            logger.warn(
                "Char image to be attached to the env is None, will exit")
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

    def save_image(self, file_name):
        """ Save character image (together with items that have been pasted on
        it), to a file.
        :param file_name: filename to be saved to as a string
        :returns: Always True (for now, wink wink)
        :rtype: Boolean
        """
        # TODO Error checking
        self._img.save(file_name)
        return True


class AvatarCategory(AvatarBase):

    @staticmethod
    def from_data(data):
        inst = None

        new_name = data['display_name']
        new_date = data['date_created']
        new_id = data['category_id']
        new_disp_ord = data['display_order']
        if 'z_index' not in data:
            new_z_ind = -1
        else:
            new_z_ind = data['z_index']
        new_sel_border = data['selected_border']
        new_hover_border = data['hover_border']
        new_active_icon = data['active_icon']
        new_inactive_icon = data['inactive_icon']

        if 'character' not in data:
            new_char = None
        else:
            new_char = data['character']

        inst = AvatarCategory(
            new_name,
            new_date,
            new_id,
            new_disp_ord,
            new_z_ind,
            new_sel_border,
            new_hover_border,
            new_active_icon,
            new_inactive_icon)

        return inst, new_char

    def __init__(self, name, date_created, cat_id, display_order,
                 z_index, sel_border, hover_border, active_icon,
                 inactive_icon):

        super(AvatarCategory, self).__init__(
            name=name, unique_id=cat_id, disp_order=display_order,
            date_created=date_created)

        self._z_index = z_index
        self._selected_border = content_dir.get_file(
            'PREVIEW_ICONS', sel_border)
        self._hover_border = content_dir.get_file(
            'PREVIEW_ICONS', hover_border)
        self._active_category_icon = content_dir.get_file(
            'ACTIVE_CATEGORY_ICONS', active_icon)
        self._inactive_category_icon = content_dir.get_file(
            'INACTIVE_CATEGORY_ICONS', inactive_icon)

        self._character = None

        self._items = {}

    def __repr__(self):
        return 'Category {}, of Character {}'.format(
            self.get_id(), self._character)

    def set_character(self, character):
        if not self._character:
            self._character = character
        else:
            logger.error(("Category '{}' is already bound to a character, "
                          "can't add {}").format(self, character))

    def get_zindex(self):
        return self._z_index

    def get_active_icon(self):
        return self._active_category_icon

    def get_inactive_icon(self):
        return self._inactive_category_icon

    def get_selected_border(self):
        return self._selected_border

    def get_hover_border(self):
        return self._hover_border

    def get_character(self):
        return self._character

    def add_item(self, item):
        if item:
            self._items[item.get_id()] = item
            item.set_category(self)
        else:
            logger.error("Item {} can't be added to Category {}".format(
                item, self))

    def item(self, item_name):
        return self._items[item_name]

    def items(self):
        # Sort by increasing order of display_order & decreasing order of date
        return sorted(self._items.itervalues(),
                      key=lambda k: (-1 * k.get_disp_order(), k.get_date()),
                      reverse=True)


class AvatarCharacterSet(object):
    """
    """
    @staticmethod
    def from_data(data):
        inst = None
        char = AvatarCharacter.from_data(data)
        if char:
            inst = AvatarCharacterSet(char)

        return inst

    def __init__(self, character):
        self._character = character
        self._categories = {}

    def __repr__(self):
        return 'Character Set of "{}"; with categories "{}"'.format(
            self._character,
            self._categories.values())

    def add_category(self, categ_obj):
        self._categories[categ_obj.get_id()] = categ_obj
        categ_obj.set_character(self.get_character())

    def get_categories(self):
        # Sort by increasing order of display_order & decreasing order of date
        return sorted(self._categories.itervalues(),
                      key=lambda k: (-1 * k.get_disp_order(), k.get_date()),
                      reverse=True)

    def get_category(self, cat_name):
        if cat_name in self._categories:
            ret_obj = self._categories[cat_name]
        else:
            ret_obj = None

        return ret_obj

    def get_character(self):
        return self._character
