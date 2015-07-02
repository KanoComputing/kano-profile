# conf_parser.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Logic for parsing and creating avatars for a Kano World profile
from kano.logging import logger
from kano_profile.badges import calculate_badges

from .character_components import (AvatarAccessory, AvatarEnvironment,
                                   AvatarCategory, AvatarCharacterSet)


class AvatarLayer(object):
    @staticmethod
    def from_data(data, char, env):
        inst = None

        char_set = AvatarCharacterSet.from_data(data)
        if char_set:
            inst = AvatarLayer()
            inst.add_character_set(char_set)
            inst.add_character_cat(char)
            inst.add_envir_cat(env)

        return inst

    def __init__(self):
        self._character_set = None
        self._character_cat = None
        self._environment_cat = None

    def __repr__(self):
        return (('Layer; character set "{}"; character category "{}"; '
                 'environment cat "{}"').format(self._character_set,
                                                self._character_cat,
                                                self._environment_cat)
                )

    def add_character_set(self, obj):
        if obj:
            self._character_set = obj
        else:
            logger.error("Character set provided is None, can't add to Layer")

    def get_id(self):
        return self._character_set.get_character().get_id()

    def add_character_cat(self, char_cat):
        if not self._character_cat:
            if char_cat:
                self._character_cat = char_cat
            else:
                logger.error(
                    "Can't add character category '{}' to layer".format(
                        char_cat))
        else:
            logger.error('Layer already has a character category')

    def add_envir_cat(self, env_cat):
        if not self._environment_cat:
            if env_cat:
                self._environment_cat = env_cat
            else:
                logger.error(
                    "Can't add environment category '{}' to layer".format(
                        env_cat))
        else:
            logger.error('Layer already has a environment category')

    def add_category(self, cat):
        self._character_set.add_category(cat)

    def category(self, cat):
        ret = None
        for c in self.get_categories():
            if c.get_id() == cat:
                ret = c
                break
        return ret

    def add_item(self, cat_name, item_obj):
        cat = self.category(cat_name)
        if cat:
            cat.add_item(item_obj)
        else:
            logger.warn(
                'Category "{}" not available in [{}], skipping "{}"'.format(
                    cat_name, self, item_obj))

    def get_categories(self):
        category_list = []
        if not self._character_cat:
            logger.error(
                "Asked for categories, but don't have characters {}".format(
                    self))
            return category_list
        else:
            if self._character_set:
                category_list = [self._character_cat]
                category_list.extend(self._character_set.get_categories())
                category_list.append(self._environment_cat)

        return category_list

    def get_object_ids(self, cat_name):
        ret = []
        cat = self.category(cat_name)
        if not cat:
            logger.error(("Category '{}' not in layer '{}', can't return"
                          "hover border").format(cat_name, self))
        else:
            ret = [k.get_id() for k in cat.items()]
        return ret

    def item(self, item_name):
        ret = None
        for k in self.get_categories():
            for it in k.items():
                if it.get_id() == item_name:
                    ret = it
                    break
            if ret:
                break
        return ret

    def character(self):
        return self._character_set.get_character()


class AvatarConfParser(object):
    """ A class to take on the important task of parsing the configuration
    file used for generating new Avatars.
    Please use this class only if you require only parsing of the
    conf file, otherwise please use the AvatarCreator() class
    """
    categories_label = 'categories'
    objects_label = 'objects'
    char_label = 'characters'
    env_label = 'environments'
    spec_cat_label = 'special_categories'
    special_category_labels = [char_label, env_label]

    def __init__(self, conf_data):
        self._layers = {}
        char_cat = None
        env_cat = None

        if self.spec_cat_label not in conf_data:
            logger.error('{} dict not found'.format(self.spec_cat_label))
        else:
            char_cat, env_cat = \
                self._populate_special_category_structures(conf_data)

        if self.char_label not in conf_data:
            logger.error('{} dict not found'.format(self.char_label))
        else:
            self._populate_layer_structures(conf_data, char_cat, env_cat)

        if self.categories_label not in conf_data:
            logger.error('{} dict not found'.format(self.categories_label))
        else:
            self._populate_cat_structures(conf_data[self.categories_label])

        if self.objects_label not in conf_data:
            logger.error('{} dict not found'.format(self.objects_label))
        else:
            self._populate_object_structures(conf_data)

        self._populate_environment_structures(conf_data, env_cat)

    def _populate_cat_structures(self, categories):
        """ Populates internal structures related to categories
        :param categories: categories section of YAML format configuration
                           structure read from file
        """
        for cat in categories:
            cat_obj, char_name = AvatarCategory.from_data(cat)
            char_layer = self.layer(char_name)
            if char_layer:
                char_layer.add_category(cat_obj)
            else:
                logger.warn(
                    ('Character layer "{}" missing, skipping category '
                     '"{}"').format(char_name, cat_obj.get_id()))

    def _populate_object_structures(self, conf_data):
        """ Populates internal structures related to items
        :param conf_data: YAML format configuration structure read from file
        """
        for obj in conf_data[self.objects_label]:
            obj, char, cat = AvatarAccessory.from_data(obj)
            char_layer = self.layer(char)
            if char_layer:
                char_layer.add_item(cat, obj)
            else:
                logger.warn(
                    ('Character layer "{}" missing, skipping item '
                     '"{}"').format(char, obj.get_id()))

    def _populate_layer_structures(self, conf_data, char, env):
        """ Populates internal structures related to characters
        :param conf_data: YAML format configuration structure read from file
        """
        for obj in conf_data[self.char_label]:
            layer = AvatarLayer.from_data(obj, char, env)
            if layer:
                self._layers[layer.get_id()] = layer
                char.add_item(layer.character())

    def _populate_environment_structures(self, conf_data, env_cat):
        """ Populates internal structures related to environments (backgrounds)
        :param conf_data: YAML format configuration structure read from file
        """
        # TODO conf_data is not used any more in this function, maybe remove it
        envirs = calculate_badges()

        for _, env in envirs[self.env_label]['all'].iteritems():
            env_obj = AvatarEnvironment.from_data(env)
            env_cat.add_item(env_obj)

    def _populate_special_category_structures(self, conf_data):
        """ Populate internal structures related to the special categories
        such as characters and environments
        :param conf_data: YAML format configuration structure read from file
        """
        special_cat_data = conf_data[self.spec_cat_label]

        for special_cat in special_cat_data:
            if special_cat['category_id'] == self.char_label:
                char, unused = AvatarCategory.from_data(special_cat)
            elif special_cat['category_id'] == self.env_label:
                env, unused = AvatarCategory.from_data(special_cat)
            else:
                logger.error("Unknown category_id in special categories")

        return char, env

    def layer(self, character_name):
        if character_name not in self._layers:
            logger.error("Character '{}' not in character layers".format(
                character_name))
            return None
        else:
            return self._layers[character_name]

    def get_zindex(self, character, category):
        """ Provides the z-index for a specific category
        :param category: The category whose z-index will be returned
        :returns: z-index as integer
        :rtype: integer
        """
        layer = self.layer(character)
        cat = layer.category(category)
        return cat.get_zindex()

    def list_available_chars(self):
        """ Provides a list of available characters
        :returns: list of characters (list of strings)
        :rtype: list of stings
        """
        return [c for c in self._layers.iterkeys()]

    def get_avail_objs(self, char, category):
        """ Provides a list of available objects for the category provided
        :returns: [] of object names
                  None if category is not found
        :rtype: list of strings or None
        """
        ret = []
        char = self.layer(char)
        if char:
            ret = char.get_object_ids(category)
        return ret

    def list_available_categories(self, character):
        """ Provides a list of available categories (not case sensitive)
        :returns: list of categories (list of strings)
        :rtype: list of strings
        """
        ret = []
        char = self.layer(character)
        if not char:
            logger.error(("Character '{}' isn't available in '{}', can't "
                          "return available categories").format(
                              character, self))
        else:
            ret = [k.get_id() for k in char.get_categories()]
        return ret

    def get_inactive_category_icon(self, character, category_name):
        """ Provides the filename of the inactive icons of the provided
        category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string
        """
        ret = None
        char = self.layer(character)
        if not char:
            logger.error(("Character '{}' isn't available in '{}', can't "
                          "return inactive cat icon").format(
                              character, self))
        else:
            ret = char.category(category_name).get_inactive_icon()
        return ret

    def get_active_category_icon(self, character, category_name):
        """ Provides the filename of the active icons of the provided category
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        ret = None
        char = self.layer(character)
        if not char:
            logger.error(("Character '{}' isn't available in '{}', can't "
                          "return active cat icon").format(
                              character, self))
        else:
            ret = char.category(category_name).get_active_icon()
        return ret

    def get_category_display_name(self, character, category_name):
        ret = ''
        char = self.layer(character)
        if not char:
            logger.error(("Character '{}' isn't availabble in '{}', can't "
                          "return display_name").format(character, self))
        else:
            ret = char.category(category_name).name()
        return ret

    def get_selected_border(self, character, category_name):
        """ Provides the filename of the selected border of the preview icon
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        ret = None
        char = self.layer(character)
        if not char:
            logger.error(("Character '{}' isn't available in '{}', can't "
                          "return selected_border").format(
                              character, self))
        else:
            ret = char.category(category_name).get_selected_border()
        return ret

    def get_hover_border(self, character, category_name):
        """ Provides the filename of the hover over border of the preview icon
        :param category_name: Category name as a string
        :returns: path to icon as string or None if category is not found
        :rtype: string or None
        """
        ret = None
        char = self.layer(character)
        if not char:
            logger.error(("Character '{}' isn't available in '{}', can't "
                          "return hover border").format(
                              character, self))
        else:
            ret = char.category(category_name).get_hover_border()
        return ret

    def get_item_preview(self, character, item_name):
        """ Provides the preview image for a given item
        :param item_name: item whose preview image will be returned
        :returns: The absolute path to the preview image as a str or
                  None if the item is not available
        :rtype: string or None
        """
        # TODO error checking
        ret = None
        char = self.layer(character)
        if not char:
            logger.error("Character blah blah")
        else:
            item = char.item(item_name)
            ret = item.get_preview_img()

        return ret

    def is_unlocked(self, character, item_name):
        """ Returns whether the item/environment is locked
        :param item_name: item whose lock status will be returned
        :returns: True iff it is unlocked
        :rtype: Boolean or None
        """
        # TODO error checking
        char = self.layer(character)
        item = char.item(item_name)
        return item.is_unlocked()
