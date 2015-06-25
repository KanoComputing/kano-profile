# logic.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Logic for parsing and creating avatars for a Kano World profile
import os
import random

from kano_avatar.paths import (AVATAR_CONF_FILE,
                               AVATAR_SCRATCH, AVATAR_DEFAULT_LOC,
                               AVATAR_DEFAULT_NAME, AVATAR_SELECTED_ITEMS)
from kano.logging import logger

from kano_profile.profile import (set_avatar, set_environment,
                                  save_profile_variable)
from kano.utils import get_date_now
from kano_content.api import ContentManager
from kano_content.extended_paths import content_dir
from json import dump, load

from .conf_parser import AvatarConfParser
# TODO Check which types of names are case sensitive


def has_selected_char(err_str):
    def decor(method):
        def check_and_call(self, *args, **kwargs):
            if not self._sel_char:
                logger.error("Character not selected, {}".format(err_str))
                return None
            else:
                return method(self, *args, **kwargs)
        return check_and_call
    return decor


class AvatarCreator(AvatarConfParser):
    """ The aim of this class is to help generate avatars for the kano world
    profile. It includes many accessor methods to get the attributes so that
    you don't have to use the internal structures.
    It has been designed and may be used from a GUI or a CLI
    Please note that when referring to items or characters, you may use their
    display name. However matching names to class objects is case sensitive.
    """

    def __init__(self, conf_data):
        super(AvatarCreator, self).__init__(conf_data)
        self._sel_char = None
        self._sel_obj = {}
        self._sel_obj_per_cat = {}
        self._sel_objs_per_zindex = {}
        self._sel_env = None

    @has_selected_char("can't return z-index")
    def get_zindex(self, cat_id):
        return super(AvatarCreator, self).get_zindex(
            self._sel_char.get_id(), cat_id)

    @has_selected_char("can't list category objects")
    def list_avail_objs(self, cat_id):
        return super(AvatarCreator, self).get_avail_objs(
            self._sel_char.get_id(), cat_id)

    @has_selected_char("can't get active category icon")
    def get_active_category_icon(self, cat_id):
        return super(AvatarCreator, self).get_active_category_icon(
            self._sel_char.get_id(), cat_id)

    @has_selected_char("can't get inactive category icon")
    def get_inactive_category_icon(self, cat_id):
        return super(AvatarCreator, self).get_inactive_category_icon(
            self._sel_char.get_id(), cat_id)

    @has_selected_char("can't get selected border")
    def get_selected_border(self, cat_id):
        return super(AvatarCreator, self).get_selected_border(
            self._sel_char.get_id(), cat_id)

    @has_selected_char("can't get hover border")
    def get_hover_border(self, cat_id):
        return super(AvatarCreator, self).get_hover_border(
            self._sel_char.get_id(), cat_id)

    @has_selected_char("can't get item preview")
    def get_item_preview(self, item_id):
        return super(AvatarCreator, self).get_item_preview(
            self._sel_char.get_id(), item_id)

    @has_selected_char("can't list available characters")
    def list_available_categories(self):
        return super(AvatarCreator, self).list_available_categories(
            self._sel_char.get_id())

    @has_selected_char("can't return lock status")
    def is_unlocked(self, obj_name):
        return super(AvatarCreator, self).is_unlocked(
            self._sel_char.get_id(), obj_name)

    def char_select(self, char_name):
        """ Set a character as a base
        :param char_name: Character name
        :returns: True iff the character exists (is available)
        :rtype: Boolean
        """
        # Get the instance of the character
        if char_name in self.list_available_chars():
            self._sel_char = self.layer(char_name).character()
            return True
        else:
            logger.error(
                'Character {} is not in the available char list'.format(
                    char_name))
            return False

    def _sel_char_layer(self):
        return self.layer(self._sel_char.get_id())

    def env_select(self, env_name):
        """ Set an environment for the background. If the environment given is
        not unlocked a different unlocked one is selected in random
        :param env_name: Environment name
        :returns: True iff the environment exists (is available)
        :rtype: Boolean
        """
        env_inst = self._sel_char_layer().item(env_name)
        if env_inst.category().get_id() == self.env_label:
            if not env_inst.is_unlocked():
                logger.warn(
                    "Environment {} is locked, replacing with random".format(
                        env_name))
                # Select randomly among the unlocked environments
                self._sel_env = random.choice(
                    [env for env in env_inst.category().items()
                        if env.is_unlocked()])
            else:
                self._sel_env = env_inst
            logger.debug(
                'Selected Environment: {}'.format(self._sel_env.get_id()))
            return True
        else:
            logger.error(
                'Environment {} is not in the available env list'.format(
                    env_name))
            return False

    def clear_env(self):
        """ Clear the selection for the environment
        """
        self._sel_env = None

    @has_selected_char("can't return path to asset")
    def selected_char_asset(self):
        """ Get the asset path for the image corresponding to the
        characted that has been selected
        :returns: the image path as a string, None if no character has been
                  selected
        :rtype: string or None
        """
        return self._sel_char.get_fname()

    def clear_sel_objs(self):
        """ Clear structures that contain items that have been selected
        """
        self._sel_obj.clear()
        self._sel_obj_per_cat.clear()
        self._sel_objs_per_zindex.clear()

    @staticmethod
    def _replace_locked(item):
        ret = item
        if not item.is_unlocked():
            logger.warn(
                ('Item {} is locked, replacing with random from '
                 'its category').format(item))
            ret = random.choice(
                [obj for obj in item.category().items() if obj.is_unlocked()]
            )
        return ret

    def set_selected_items(self, obj_names):
        for obj in obj_names:
            if obj in self.list_available_chars():
                self.char_select(obj)
                break

        obj_list = [it for it in obj_names
                    if self._sel_char_layer().item(it)]

        self.randomise_rest(obj_list)

    def obj_select(self, obj_names, clear_existing=True):
        """ Specify the items to be used for the character. if any of the
        items are locked, replace with a different unlocked one from the
        same category.
        :param obj_names: list of item names
        :returns: False if any of the objects doesn't exist or if there are
                  multiple items from the same category are selected.
        :rtype: Boolean
        """
        if clear_existing:
            self.clear_sel_objs()
            self.clear_env()

        sel_env_flag = False

        for obj_name in obj_names:
            if not self._sel_char_layer().item(obj_name):
                logger.error(
                    'Object "{}" not available for character {}'.format(
                        obj_name, self._sel_char))
                return False
            else:
                obj_inst = self._sel_char_layer().item(obj_name)
                obj_inst = self._replace_locked(obj_inst)
                if obj_inst.category().get_id() != self.env_label and \
                        obj_inst.category().get_id() != self.char_label:
                    # Check whether we have selected multiple items from
                    # the same category
                    if obj_inst.category().get_id() in self._sel_obj_per_cat:
                        logger.error(
                            'Multiple objects in category {}'.format(
                                obj_inst.category()))
                        return False

                    obj_cat = obj_inst.category().get_id()
                    self._sel_obj_per_cat[obj_cat] = obj_inst
                    self._sel_obj[obj_inst.get_id()] = obj_inst

                    # Create a dictionary with which objects belong to
                    # each z-index
                    obj_zindex = obj_inst.category().get_zindex()
                    if obj_zindex not in self._sel_objs_per_zindex:
                        self._sel_objs_per_zindex[obj_zindex] = []

                    self._sel_objs_per_zindex[obj_zindex].append(obj_inst)

                elif obj_inst.category().get_id() == self.env_label:
                    # Deal with the object if it is an environment
                    if not sel_env_flag:
                        self.env_select(obj_name)
                        sel_env_flag = True
                    else:
                        logger.error(
                            ("Provided multiple environments to select "
                             "{}, {}").format(
                                self._sel_env.get_id(), obj_name))
                        return False
        return True

    def randomise_rest(self, obj_names, empty_cats=False):
        """ Add specified objects and randomise the remaining ones
        :param obj_names: list of item names
        :param empty_cats: (Optional) set to True if it is acceptable to get
                           categories without any objects.
        :returns: False if any of the objects doesn't exist or if there are
                  multiple items from the same category are selected.
        :rtype: Boolean
        """
        random_item_names = []
        # Select ones we definitely want
        rc = self.obj_select(obj_names)
        if not rc:
            return False
        # For categories where we haven't specified, select randomly
        avail_cats = (cat.get_id()
                       for cat in self._sel_char_layer().get_categories()
                       if cat.get_id() != self.char_label)
        for cat in set(avail_cats).difference(
                    set(self._sel_obj_per_cat.keys())):
            # Need to make sure that we can handle categories that contain no
            # items
            try:
                available_objs = [obj
                                  for obj in self._sel_char_layer().category(cat).items()
                                  if obj.is_unlocked()]
                if empty_cats:
                    available_objs.append(None)
                choice = random.choice(available_objs)
                if choice:
                    random_item_names.append(choice.get_id())
            except KeyError:
                log_msg = "Category {} doesn't contain any items".format(cat)
                logger.debug(log_msg)
                continue

        rc = self.obj_select(random_item_names, clear_existing=False)

        if not rc:
            return False
        return True

    def randomise_all_items(self):
        """ Randomise all items for a character
        :returns: A list of the selected items
        :rtype: List of strings
        """
        self.randomise_rest('')
        return self.selected_items_per_cat()

    def selected_char(self):
        if self._sel_char:
            return self._sel_char.get_id()
        else:
            return ""

    def selected_items(self):
        """ Returns a list of the items that have been selected
        :returns: A list of the selected items
        :rtype: list of strings
        """
        ret = self._sel_obj.keys()
        # if there is an env selected, append it to the list to be returned
        if self._sel_env:
            ret.append(self._sel_env.get_id())
        return ret

    def selected_items_per_cat(self):
        """ Returns a dictionary of the selected items organised by their
        category.
        :returns: A dict with [categ_labels] -> item_selected
        :rtype: dict
        """
        ret = {cat: item.get_id()
               for cat, item in self._sel_obj_per_cat.iteritems()}
        ret[self.env_label] = self._sel_env.get_id()
        return ret

    def create_avatar(self, file_name=''):
        """ Create the finished main image and save it to file.
        :param file_name: (Optional) A filename to be used for the asset that
                          is generated
        :returns: None if there was an issue while creating avatar, the
                  location of the created file otherwise
        :rtype: String or None
        """
        logger.debug(
            'About to create character with items: {}'.format(
                str(self.selected_items()))
        )
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
        """ Provides the default full path and filename for the final image
        that includes the environment
        :returns: Full path and filename
        :rtype: string
        """
        dn = os.path.join(
                os.path.abspath(os.path.expanduser(AVATAR_DEFAULT_LOC)),
                AVATAR_DEFAULT_NAME)
        return append_suffix_to_fname(dn, '_inc_env')

    def create_auxiliary_assets(self, file_name):
        """ Creates all of the auxiliary assets. This is to be used after the
        user has finalised his choices and we are about to synchronise with
        Kano World
        :param file_name: To be used as the base for generating the filenames
                          of the other assets
        :returns: False iff the generation of any of the assets fails
        :rtype: Boolean
        """
        logger.debug(
            'About to create auxiliary assets with items: {}'.format(
                str(self.selected_items()))
        )
        # Avatar on its own
        rc = self.save_image(file_name)
        if not rc:
            logger.error(
                "Couldn't save character, aborting auxiliary asset generation")
            return False

        # Circular assets
        fname_circ = append_suffix_to_fname(file_name, '_circ_ring')
        fname_plain = append_suffix_to_fname(file_name, '_circ_plain')
        rc_c = self.create_circular_assets(fname_plain, fname_circ)
        if not rc_c:
            logger.error(
                ("Couldn't create circular assets, aborting auxiliary "
                 "asset generation"))
            return False

        # Environment + avatar
        fname_env = append_suffix_to_fname(file_name, '_inc_env_page2')
        rc_env = self._sel_env.save_image(fname_env)
        if not rc_env:
            logger.error(
                ("Couldn't create environment asset, aborting auxiliary "
                 "asset generation"))
            return False
        # Shifted environment
        fname_env_23 = append_suffix_to_fname(file_name, '_inc_env_page2')
        rc_23 = self.create_avatar_with_background(fname_env_23,
                                                   x_offset=0.33,
                                                   reload_img=True)
        if not rc_23:
            logger.error(
                ("Couldn't create shifted environment asset, aborting "
                 "auxiliary asset generation"))
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
        :rtype: Boolean
        """
        dn = os.path.abspath(os.path.expanduser(dir_name))

        direc = os.path.dirname(dn)
        # if the path to file does not exist, create it
        if not os.path.isdir(direc):
            os.makedirs(direc)

        if not self._compare_existing_to_new(AVATAR_SELECTED_ITEMS):
            self._write_char_log_file(AVATAR_SELECTED_ITEMS)

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
        else:
            logger.info(
                'Assets for avatar already exist, will skip creating them')

        if sync:
            items_no_env = self.selected_items_per_cat()
            items_no_env.pop(self.env_label, None)
            # When saving a new character in the profile, ensure that
            # the right version is used to sync with the API
            save_profile_variable('version', 2)
            set_avatar(self._sel_char.get_id(), items_no_env)
            set_environment(self._sel_env.get_id(), sync=True)

        return True

    def _write_char_log_file(self, fname):
        """ Creates a file that includes the avatar configuration used when
        the rest of the assets where created as a label. The purpose of this
        file is to avoid the time consuming process of recreating assets that
        are already present and updated.
        :param fname: filename for the configuration file to be created
        :returns: False iff some error occurs
        :rtype: Boolean
        """
        if self._sel_char is None:
            logger.warn(
                'Character not selected, will abandon writing log file')
            return False

        if self._sel_env is None:
            logger.warn(
                'Environment not selected, will abandon writing log file')
            return False

        created_file = False
        with open(fname, 'w') as fp:
            obj_av = {}
            # ensure that environments is not present in this dict
            items = self.selected_items_per_cat()
            items.pop(self.env_label, None)
            obj_av['avatar'] = [self._sel_char.get_id(), items]
            obj_av['environment'] = self._sel_env.get_id()
            obj_av['date_created'] = get_date_now()
            dump(obj_av, fp)
            created_file = True

        return created_file

    def _compare_existing_to_new(self, dirname):
        """ Compares the currently selected set of items, character,
        environment to the ones that are listed in the file that is provided.
        If it they match, it returns True, else False. This may be used to
        check whether assets already exist to as to avoid recreating them (a
        process that takes significant time)
        :param dirname: File where character log is stored
        :returns: True iff what is in the file correspond to what is currently
                  selected
        :rtype: Boolean
        """
        already_exists = False

        if not os.path.isfile(dirname):
            logger.debug("Character log file doesn't exist")
            return False

        with open(dirname, 'r') as fp:
            fp = open(dirname, 'r')
            log_ex = load(fp)
            try:
                char_ex, items_ex = log_ex['avatar']
                env_ex = log_ex['environment']
                # First check if environment and character match
                if char_ex == self._sel_char.get_id() and \
                   env_ex == self._sel_env.get_id():
                    items_now = self.selected_items_per_cat()
                    # Check if the no of catefories match
                    if len(items_now) == len(items_ex):
                        aligned_count = 0
                        # Check if all category -> selection pairs match
                        for key_ex, value_ex in items_ex.iteritems():
                            if items_now[key_ex] != value_ex:
                                break
                            else:
                                aligned_count += 1
                        if aligned_count == len(items_ex):
                            already_exists = True
            except KeyError as e:
                logger.info(
                    "Cats or fields don't match, problematic key {}".format(e))

        return already_exists

    def create_avatar_with_background(self, file_name, x_offset=0.5,
                                      y_offset=0.5, reload_img=False):
        """ Generates and saves the final image together with the background
        :param file_name: name of the file to save the image to
        :param x_offset: offset (as a percentage) of the avatar on the x axis
        :param y_offset: offset (as a percentage) of the avatar on the y axis
        :param reload_img: Set to True to reset the image with the selected
                           background
        :returns: Always True for now
        :rtype: Boolean
        """
        if reload_img:
            self._sel_env.load_image()

        # TODO can perform error checking here
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
        :rtype: None or Boolean
        """
        # TODO Return False instead of None in case of error
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
        """ Load the character and environment images
        :returns: True iff the character exists
        :rtype: Boolean
        """
        if self._sel_char is None:
            logger.error("You haven't specified a character")
            return False
        # TODO check if the environment has been selected as well

        self._sel_char.load_image()
        self._sel_env.load_image()
        return True

    def save_image(self, file_name):
        """ Save image as a file
        :param file_name: Filename of the new file
        :returns: False if the a character hasn't been selected
                  True otherwise
        :rtype: Boolean
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


def get_avatar_conf(aux_files=[]):
    conf = None

    cm = ContentManager.from_local()
    for k in cm.list_local_objects(spec='kano-content-category'):
        content_dir.register_path(
            'ACTIVE_CATEGORY_ICONS', k.get_data('active_cat_icon').get_dir())
        content_dir.register_path(
            'INACTIVE_CATEGORY_ICONS',
            k.get_data('inactive_cat_icon').get_dir())
        content_dir.register_path(
            'PREVIEW_ICONS', k.get_data('previews').get_dir())
        content_dir.register_path('ITEM_DIR', k.get_data('assets').get_dir())
        aux_files.append(k.get_data('').get_content()[0])

    with open(AVATAR_CONF_FILE) as f:
        conf = load(f)

    if conf is None:
        logger.error('Default Conf file {} not found'.format(AVATAR_CONF_FILE))
    else:
        if not is_valid_configuration(conf):
            logger.error('Default configuration file is not in valid format')
            return dict()

    if aux_files:
        logger.debug(
            'Auxiliary configuration files to be used: {}'.format(aux_files))

        for con_fname in aux_files:
            if os.path.isfile(con_fname):
                # Attempt to decode as JSON
                try:
                    f = open(con_fname)
                except IOError as e:
                    logger.error(
                        'Error opening the aux conf file {}'.format(e))
                    continue
                else:
                    with f:
                        try:
                            aux_conf = load(f)
                        except ValueError as e:
                            logger.info('Conf file not a JSON {}'.format(e))
                            continue

                if is_valid_configuration(aux_conf):
                    if not merge_conf_files(conf, aux_conf):
                        logger.error(
                            "Can't integrate conf file {}".format(con_fname))
                else:
                    logger.error(
                        "Parsed auxiliary film doesn't contain valid conf")
            else:
                logger.warn(
                    "Auxiliary conf file {} doen't exist".format(con_fname))
    return conf


def is_valid_configuration(conf_struct):
    allowed_conf = set(
        ('special_categories',
         'objects',
         'categories',
         'characters')
    )
    if set(conf_struct.iterkeys()).issubset(allowed_conf):
        pass
    else:
        logger.error('Conf structure contains invalid objects')
        return False
    return True


def merge_conf_files(conf_base, conf_added):
    """
    """
    if not is_valid_configuration(conf_base) or \
            not is_valid_configuration(conf_added):
        return None
    else:
        for cat in conf_added.iterkeys():
            if cat in conf_base:
                if type(conf_base[cat]) != type(conf_added[cat]):
                    logger.error(
                        'base and auxiliary configuration types mismatch')
                    return None
                else:
                    if type(conf_base[cat]) == list:
                        conf_base[cat] += conf_added[cat]
                    elif type(conf_base[cat]) == dict:
                        conf_base[cat].update(conf_added[cat])
                    else:
                        logger.warning(
                            "Can't handle type {}".format(conf_base[cat]))
                        return None
            else:
                conf_base[cat] = conf_added[cat]
    return True
