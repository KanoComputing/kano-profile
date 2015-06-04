# conf_parser.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Logic for parsing and creating avatars for a Kano World profile
from kano.logging import logger
from kano_profile.badges import calculate_badges

from .character_components import (AvatarAccessory, AvatarCharacter,
                                   AvatarEnvironment)
from kano_content import content_dir


class AvatarConfParser:
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
            active_icon_file = content_dir.get_file(
                'ACTIVE_CATEGORY_ICONS', icon_file)
            inactive_icon_file = content_dir.get_file(
                'INACTIVE_CATEGORY_ICONS', icon_file)

            selected_border_file = content_dir.get_file(
                'PREVIEW_ICONS', cat['selected_border'])
            hover_border_file = content_dir.get_file(
                'PREVIEW_ICONS', cat['hover_border'])
            self._active_category_icons[cat['cat_name']] = active_icon_file
            self._inactive_category_icons[cat['cat_name']] = inactive_icon_file
            self._selected_borders[cat['cat_name']] = selected_border_file
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
            # TODO hardcoded all unlocked for items until we change them to
            # use the same scheme as environments
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
            # TODO hardcoded all unlocked for characters until we change them
            # to use the same scheme as environments
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
        # TODO conf_data is not used any more in this function, maybe remove it
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
            active_icon_file = content_dir.get_file(
                'ACTIVE_SPECIAL_CATEGORY_ICONS',
                special_cat_data[special_cat]['active_icon'])

            inactive_icon_file = content_dir.get_file(
                'INACTIVE_SPECIAL_CATEGORY_ICONS',
                special_cat_data[special_cat]['inactive_icon'])

            border_icon_file = content_dir.get_file(
                'PREVIEW_ICONS',
                special_cat_data[special_cat]['selected_border'])

            hover_icon_file = content_dir.get_file(
                'PREVIEW_ICONS',
                special_cat_data[special_cat]['hover_border'])

            self._active_special_category_icons[special_cat] = active_icon_file
            self._inactive_special_category_icons[special_cat] = \
                inactive_icon_file
            self._border_special_cat[special_cat] = border_icon_file
            self._hover_border_special_cat[special_cat] = hover_icon_file
            self._special_cat_to_disp_order[special_cat] = \
                special_cat_data[special_cat]['display_order']

    def get_zindex(self, category):
        """ Provides the z-index for a specific category
        :param category: The category whose z-index will be returned
        :returns: z-index as integer
        :rtype: integer
        """
        if category not in self._cat_to_z_index:
            logger.warn('Category {} not in available ones'.format(category))
        else:
            return self._cat_to_z_index[category]

    def _get_reg_item_cat(self, item_name):
        """ Get the category of an item if that item belongs to a regular
        category
        :param item_name: Item whose category will be returned
        :returns: category as a string
        :rtype: string or None
        """
        if item_name in self._objects:
            return self._objects[item_name].category()
        else:
            return None

    def get_item_category(self, item_name):
        """ Get the category of an item/environment if that item/env exists
        :param item_name: item/env name whose category will be returned
        :returns: category as a string or None
        :rtype: string or None
        """
        cat_label = self._get_reg_item_cat(item_name)
        if not cat_label:
            if item_name not in self._environments:
                logger.warn('Item {} neither in obj nor in env list'.format(
                    item_name))
                return None
            else:
                cat_label = self.env_label
        return cat_label

    def list_available_chars(self):
        """ Provides a list of available characters
        :returns: list of characters (list of strings)
        :rtype: list of stings
        """
        return [k for k in self._characters.keys()]

    def _list_all_available_regular_objs(self):
        """ Provides a list of available regular objects
        :returns: list of objects (list of strings)
        :rtype: list of strings
        """
        return [k for k in self._objects.keys()]

    def list_all_available_environments(self):
        """ Provides a list of available environments
        :returns: list of environments (list of strings)
        :rtype: list of strings
        """
        env_inst_ord = sorted(self._environments.itervalues(),
                              key=lambda env: env.get_disp_order())
        return [k.name() for k in env_inst_ord]

    def list_all_available_objs(self):
        """ Provides a list of available objects
        :returns: list of objects (list of strings)
        :rtype: list of strings
        """
        ret = self._list_all_available_regular_objs()
        ret.extend(self.list_all_available_environments())
        return ret

    def _get_avail_objs_regular_cat(self, category):
        """ Provides a list of available objects for the specific normal category
        :returns: [] of object names
                  None if category is not found
        :rtype: list of strings or None
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
        :rtype: list of strings or None
        """
        if category == self.env_label:
            return self.list_all_available_environments()
        else:
            return self._get_avail_objs_regular_cat(category)

    def _list_available_regular_categories(self):
        """ Provides a list of available regular categories (not case
        sensitive)
        :returns: list of categories (list of strings)
        :rtype: list of strings
        """
        reg_cats_ord = sorted(self._cat_to_disp_order.iteritems(),
                              key=lambda k: k[1])
        return [k[0] for k in reg_cats_ord]

    def _list_available_special_categories(self):
        """ Provides a list of available special categories (not case
        sensitive)
        :returns: list of categories (list of strings)
        :rtype: list of strings
        """
        # TODO Temporary hardcoding
        # return self.special_category_labels
        # At the time it is only one so it is sorted
        return [self.env_label]

    def list_available_categories(self):
        """ Provides a list of available categories (not case sensitive)
        :returns: list of categories (list of strings)
        :rtype: list of strings
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
        :rtype: string
        """
        icon_path = self._get_inactive_reg_category_icon(category_name) or \
            self._get_inactive_special_category_icon(category_name)

        if not icon_path:
            logger.warn(
                "Cat {} not found, can't provide inactive icon path".format(
                    category_name)
            )
        return icon_path

    def _get_inactive_reg_category_icon(self, category_name):
        """ Provides the filename of the active icons of the provided
        regular category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        if category_name not in self._inactive_category_icons:
            return None
        else:
            return self._inactive_category_icons[category_name]

    def get_active_category_icon(self, category_name):
        """ Provides the filename of the active icons of the provided category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        icon_path = self._get_active_reg_category_icon(category_name) or \
            self._get_active_special_category_icon(category_name)

        if not icon_path:
            logger.warn(
                "Cat {} not found, can't provide active icon path".format(
                    category_name)
            )

        return icon_path

    def _get_active_reg_category_icon(self, category_name):
        """ Provides the filename of the active icons of the provided active
        category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        if category_name not in self._active_category_icons:
            return None
        else:
            return self._active_category_icons[category_name]

    def get_selected_border(self, category_name):
        """ Provides the filename of the selected border of the preview icon
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        icon_path = self._get_selected_border_regular(category_name) or \
            self._get_selected_border_special(category_name)
        if not icon_path:
            logger.warn(
                "Cat {} not found, can't provide selected border path".format(
                    category_name)
            )

        return icon_path

    def _get_selected_border_regular(self, category_name):
        """ Provides the filename of the selected border of the preview icon
        :param category_name: Regular category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        if category_name not in self._selected_borders:
            return None
        else:
            return self._selected_borders[category_name]

    def get_hover_border(self, category_name):
        """ Provides the filename of the hover over border of the preview icon
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        icon_path = self._get_hover_border_regular(category_name) or \
            self._get_hover_border_special(category_name)

        if not icon_path:
            logger.warn(
                "Cat {} wasn't found, can't provide hover border path".format(
                    category_name)
            )
        return icon_path

    def _get_hover_border_regular(self, category_name):
        """ Provides the filename of the hover border of the preview icon
        :param category_name: Regular category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        if category_name not in self._hover_borders:
            return None
        else:
            return self._hover_borders[category_name]

    def _get_inactive_special_category_icon(self, special_category_name):
        """ Provides the filename of the active icons of the provided category
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        if special_category_name not in self._inactive_special_category_icons:
            return None
        else:
            return self._inactive_special_category_icons[special_category_name]

    def _get_active_special_category_icon(self, special_category_name):
        """ Provides the filename of the inactive icons of the provided category
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        if special_category_name not in self._active_special_category_icons:
            return None
        else:
            return self._active_special_category_icons[special_category_name]

    def _get_selected_border_special(self, special_category_name):
        """ Provides the filename of the selected border of the preview icon
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        self._border_special_cat
        if special_category_name not in self._border_special_cat:
            return None
        else:
            return self._border_special_cat[special_category_name]

    def _get_hover_border_special(self, special_category_name):
        """ Provides the filename of the hover border of the preview icon
        :param special_category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        if special_category_name not in self._hover_border_special_cat:
            return None
        else:
            return self._border_special_cat[special_category_name]

    def get_char_preview(self, char_name):
        """ Provides the preview image for a given character
        :param char_name: Character whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the character is not available
        :rtype: string or None
        """
        if char_name not in self._characters:
            logger.warn(
                "Char {} not in avail chars, can't return preview img".format(
                    char_name))
            return None
        else:
            return self._characters[char_name].get_preview_img()

    def get_item_preview(self, item_name):
        """ Provides the preview image for a given item
        :param item_name: item whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the item is not available
        :rtype: string or None
        """
        prev_img = self._get_reg_item_preview(item_name) or \
            self._get_environment_preview(item_name)

        if not prev_img:
            logger.warn(
                "Item {} not in avail objs, can't return preview img".format(
                    item_name)
            )
        return prev_img

    def _get_reg_item_preview(self, item_name):
        """ Provides the preview image for a given regular item
        :param item_name: item whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the item is not available
        :rtype: string or None
        """
        if item_name not in self._objects:
            return None
        else:
            return self._objects[item_name].get_preview_img()

    def _get_environment_preview(self, environment_name):
        """ Provides the preview image for a given environment
        :param environment_name: environment whose preview image will be
                                 returned
        :returns: The absolute path to the preview image as a str or
                  None if the environment is not available
        :rtype: string or None
        """
        if environment_name not in self._environments:
            return None
        else:
            return self._environments[environment_name].get_preview_img()

    def is_unlocked(self, item_name):
        """ Returns whether the item/environment is locked
        :param item_name: item whose lock status will be returned
        :returns: True iff it is unlocked
        :rtype: Boolean or None
        """
        lock_state = self._is_unlocked_reg_item(item_name)

        if lock_state is None:
            lock_state = self._is_unlocked_env(item_name)

        if lock_state is None:
            logger.warn(
                "Item {} not in avail objs/envs, can't return lock state".format(
                    item_name)
            )

        return lock_state

    def _is_unlocked_reg_item(self, item_name):
        """ Get lock state of an item which belongs to a regular category
        :param item_name: Item whose lock state will be returned
        :retuns: Lock state or None if item doesn't belong to a regular category
        :rtype: Boolean or None
        """
        if item_name not in self._objects:
            return None
        else:
            return self._objects[item_name].is_unlocked()

    def _is_unlocked_env(self, item_name):
        """ Get lock state of an environment
        :param item_name: env whose lock state will be returned
        :retuns: Lock state or None if item isn't an environment
        :rtype: Boolean or None
        """
        if item_name not in self._environments:
            return None
        else:
            return self._environments[item_name].is_unlocked()
