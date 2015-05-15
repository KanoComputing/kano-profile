#!/usr/bin/env python

# session.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import requests

# TODO: Remove this statement after upgrading to a friendly Python-requests match
requests.packages.urllib3.disable_warnings()

import json
import os

from kano.logging import logger
from kano.utils import download_url, read_json, ensure_dir, chown_path
from kano_profile.profile import (load_profile, set_avatar, set_environment,
                                  save_profile, save_profile_variable,
                                  recreate_char)
from kano_profile.badges import calculate_xp
from kano_profile.apps import get_app_list, load_app_state, save_app_state
from kano_profile.paths import app_profiles_file, online_badges_dir, \
    online_badges_file, profile_dir
from kano_profile.tracker import get_tracker_events, clear_tracker_events
from kano_profile_gui.paths import media_dir
from kano_avatar.paths import (AVATAR_DEFAULT_LOC, AVATAR_DEFAULT_NAME,
                               AVATAR_ENV_DEFAULT,
                               AVATAR_CIRC_PLAIN_DEFAULT)

from .connection import request_wrapper, content_type_json

app_profiles_data = read_json(app_profiles_file)


def is_private(app_name):
    try:
        private = app_profiles_data[app_name]['private']
    except Exception:
        private = False
    return private


class KanoWorldSession(object):
    session = requests.Session()

    def __init__(self, token):
        self.session.headers.update({'Authorization': token})
        success, text, _ = self.test_auth()
        if not success:
            raise Exception(text)

    def test_auth(self):
        return request_wrapper('get', '/auth/session', session=self.session)

    def upload_profile_stats(self):
        profile = load_profile()

        data = dict()

        # xp
        data['xp'] = calculate_xp()

        # version
        try:
            data['version'] = profile['version']
        except KeyError:
            logger.debug("Version field not in the data to be synced")

        # age
        try:
            data['birthdate'] = profile['birthdate']
        except Exception:
            pass

        # gender
        try:
            gender = profile['gender']
            if gender == 'Boy':
                gender = 'm'
            elif gender == 'Girl':
                gender = 'f'
            elif gender == "Wizard":
                gender = 'x'
            data['gender'] = gender
        except Exception:
            pass

        # avatar_generator
        data, files = self._prepare_avatar_gen(profile, data)
        # app states
        stats = dict()
        for app in get_app_list():
            if not is_private(app):
                stats[app] = load_app_state(app)

        # append stats
        data['stats'] = stats

        # Uploading profile stats
        success, text, response_data = request_wrapper(
            'put',
            '/users/profile',
            data=json.dumps(data),
            headers=content_type_json,
            session=self.session)

        if not success:
            logger.error('Uploading of the profile data failed')
            return False, text

        if files:
            # Uploading avatar assets
            success, text, response_data = request_wrapper(
                'put',
                '/users/profile',
                session=self.session,
                files=files)

            # requests doesn't close the file objects after sending them, so
            # we need to tidy up
            self._tidy_up_avatar_files(files)

            if not success:
                logger.error('Uploading of the avatar assets failed')
                return False, text

        return self.download_profile_stats(response_data)

    def _prepare_avatar_gen(self, profile_data, data_to_send):
        files = {}
        if ('version' not in profile_data or
                profile_data['version'] == 1):
            try:
                avatar_generator = {
                    'character': profile_data['avatar'],
                    'environment': ['all', profile_data['environment']]
                }
                data_to_send['avatar_generator'] = avatar_generator
            except Exception:
                pass
        elif profile_data['version'] == 2:
            # In this version we need to add a field that indicates
            # that this is version 2. Furthermore we need to uplodad
            # the new assets to the server
            try:
                avatar_generator = {
                    'version': 2,
                    'character': profile_data['avatar'],
                    'environment': ['all', profile_data['environment']]
                }
                data_to_send['avatar_generator'] = avatar_generator
                path_circ = os.path.join(
                    AVATAR_DEFAULT_LOC,
                    AVATAR_CIRC_PLAIN_DEFAULT)
                path_env = os.path.join(
                    AVATAR_DEFAULT_LOC,
                    AVATAR_ENV_DEFAULT)
                path_char = os.path.join(
                    AVATAR_DEFAULT_LOC,
                    AVATAR_DEFAULT_NAME)
                files = {
                    'avatar_circle': open(path_circ, 'rb'),
                    'avatar_landscape': open(path_env, 'rb'),
                    'avatar_character': open(path_char, 'rb')
                }
            except KeyError as e:
                logger.debug('Attribute {} not found in profile'.format(e))
            except IOError as e:
                # There was an error somewhere, do not upload files
                files = {}
                logger.error(
                    'Error opening 1 of the files to upload {}'.format(str(e))
                )
            except Exception:
                pass
        else:
            logger.debug(
                "Unknown profile ver: {}, can't upload data".format(
                    profile_data['version'])
                )
        return data_to_send, files

    def _tidy_up_avatar_files(self, files):
        try:
            for f in files.itervalues():
                f.close()
        except Exception:
            logger.debug("Error closing avatar files")

    def download_profile_stats(self, data=None):
        if not data:
            profile = load_profile()
            if 'kanoworld_id' in profile:
                user_id = profile['kanoworld_id']
            else:
                return False, 'Profile not registered!'

            success, text, data = request_wrapper('get', '/users/' + user_id,
                                                  headers=content_type_json,
                                                  session=self.session)
            if not success:
                return False, text

        try:
            version_no = data['user']['avatar']['generator']['version']
            save_profile_variable('version', version_no)
        except Exception:
            pass

        updated_locally = False
        try:
            # Only update locally if version is 2. otherwise we will generate
            # a default
            if data['user']['avatar']['generator']['version'] == 2:
                gen = data['user']['avatar']['generator']
                avatar_subcat, avatar_item = gen['character']
                updated_locally = set_avatar(avatar_subcat, avatar_item)

                environment = gen['environment'][1]
                updated_locally |= set_environment(environment)

        except Exception:
            pass

        # app states
        try:
            app_data = data['user']['profile']['stats']
        except Exception:
            return False, 'Data missing from payload!'

        for app, values in app_data.iteritems():
            if not values or \
                    (len(values.keys()) == 1 and 'save_date' in values):
                continue
            if not is_private(app):
                save_app_state(app, values)

        if updated_locally:
            recreate_char(block=True)

        return True, None

    def upload_private_data(self):
        data = dict()
        for app in get_app_list():
            if is_private(app):
                data[app] = load_app_state(app)

        payload = dict()
        payload['data'] = data

        success, text, data = request_wrapper('put', '/sync/data',
                                              data=json.dumps(payload),
                                              headers=content_type_json,
                                              session=self.session)
        if not success:
            return False, text

        return self.download_private_data(data)

    def download_private_data(self, data=None):
        if not data:
            success, text, data = request_wrapper('get', '/sync/data',
                                                  headers=content_type_json,
                                                  session=self.session)
            if not success:
                return False, text

        if 'user_data' in data and 'data' in data['user_data']:
            app_data = data['user_data']['data']
        else:
            return False, 'Data missing missing from payload!'

        for app, values in app_data.iteritems():
            if is_private(app):
                save_app_state(app, values)
        return True, None

    def backup_content(self, file_path):
        if not os.path.exists(file_path):
            return False, 'File path not found!'

        try:

            files = {'file': open(file_path, 'rb')}

            success, text, data = request_wrapper('put', '/sync/backup',
                                                  session=self.session,
                                                  files=files)
        except IOError as e:
            # There was an error somewhere, do not upload files
            files = {}
            text = 'Error opening 1 of the files to backup {}'.format(str(e))
            success = False

        if not success:
            return False, text

        success = 'success' in data and data['success']
        if not success:
            return False, 'Backup not successful!'
        return True, None

    def restore_content(self, file_path):
        success, text, data = request_wrapper('get', '/sync/backup',
                                              session=self.session)
        if not success:
            return False, text

        try:
            file_url = data['user_backup']['file_url']
        except Exception:
            file_url = None

        if not file_url:
            return False, 'backup file not found'

        return download_url(file_url, file_path)

    def upload_share(self, file_path, title, app_name, featured):
        if not os.path.exists(file_path):
            return False, 'File path not found: {}'.format(file_path)

        extensionless_path = os.path.splitext(file_path)[0]

        # attachment
        try:
            files = {
                'attachment': open(file_path, 'rb'),
            }

            # List of attachments to search for in (name, extension) format
            attachment_files = [
                ('cover', 'png'),
                ('resource', 'tar.gz'),
                ('sample', 'mp3')
            ]

            for attachment in attachment_files:
                key, ext = attachment
                attachment_path = "{}.{}".format(extensionless_path, ext)

                if os.path.exists(attachment_path):
                    logger.debug(
                        'uploading {}: {}'.format(key, attachment_path))
                    files[key] = open(attachment_path, 'rb')

        except IOError as e:
            files = None
            txt = 'Error opening the files to be shared {}'.format(str(e))

        # Since we can't open the file, there is no need to continue
        if not files:
            return False, txt

        # data
        payload = {
            'title': title,
            'featured': featured
        }

        # description
        jsonfile_path = '{}.json'.format(extensionless_path)
        try:
            description = read_json(jsonfile_path)['description']
            logger.debug('uploading json: {}'.format(jsonfile_path))
            payload['description'] = description
        except Exception:
            description = None

        logger.debug('uploading payload: {}'.format(payload))
        logger.debug('uploading files: {}'.format(files))

        endpoint = '/share/{}'.format(app_name)

        success, text, data = request_wrapper('post', endpoint,
                                              session=self.session,
                                              files=files, data=payload)
        if not success:
            return False, text

        success = 'success' in data and data['success']
        if not success:
            return False, 'Share upload not successful!'
        return True, None

    def delete_share(self, share_id):
        endpoint = '/share/{}'.format(share_id)

        success, text, data = request_wrapper('delete', endpoint,
                                              session=self.session)
        if not success:
            return False, text
        return True, None

    def refresh_notifications(self):
        rv = True
        error = None

        next_page = 0
        notifications = []
        while next_page is not None:
            success, text, data = request_wrapper(
                'get',
                '/notifications?read=false&page={}'.format(next_page),
                session=self.session
            )

            if not success:
                rv = False
                error = text
                break

            for entry in data['entries']:
                if entry['read'] is False:
                    n = self._process_notification(entry)
                    notifications.append(n)

            try:
                next_page = data['next']
            except:
                break

        if rv:
            profile = load_profile()
            profile['notifications'] = notifications
            save_profile(profile)

        return rv, error

    def upload_tracking_data(self):
        data = get_tracker_events(old_only=True)
        if len(data['events']) == 0:
            return True, "No data available"

        success, text, response_data = request_wrapper(
            'post',
            '/tracking',
            headers=content_type_json,
            session=self.session,
            data=json.dumps(data)
        )

        if success and 'success' in response_data and response_data['success']:
            clear_tracker_events(old_only=True)
            return True, None

        return False, "Upload failed, tracking data not sent."

    def download_online_badges(self):
        profile = load_profile()
        if 'kanoworld_id' in profile:
            user_id = profile['kanoworld_id']
        else:
            return False, 'Profile not registered!'

        success, text, data = request_wrapper(
            'get', '/users/{}'.format(user_id),
            session=self.session
        )

        if not success:
            return False, text

        if "user" not in data:
            return False, "Corrupt response (the 'user' key not found)"

        if "profile" not in data["user"]:
            return False, "Corrupt response (the 'user.profile' key not found)"

        if "badges" not in data["user"]["profile"]:
            msg = "Corrupt response (the 'user.profile.badges' key not found)"
            return False, msg

        online_badges_data = {}

        ensure_dir(online_badges_dir)

        badges = data["user"]["profile"]["badges"]
        for badge in badges:
            if "assigned" not in badge or not badge["assigned"]:
                continue

            if "image_url" not in badge:
                return False, "Couldn't find an image for the badge"

            image_loc = os.path.join(online_badges_dir,
                                     "{}.png".format(badge["id"]))
            download_url(badge["image_url"], image_loc)

            online_badges_data[badge["id"]] = {
                "achieved": True,
                "bg_color": badge["bg_color"].replace("#", ""),
                "desc_locked": badge["desc_locked"],
                "desc_unlocked": badge["desc_unlocked"],
                "title": badge["title"]
            }

        try:
            may_write = True
            txt = None
            f = open(online_badges_file, "w")
        except IOError as e:
            may_write = False
            txt = 'Error opening badges file {}'.format(str(e))
        else:
            with f:
                f.write(json.dumps(online_badges_data))
            if 'SUDO_USER' in os.environ:
                chown_path(online_badges_dir)
                chown_path(online_badges_file)


        return may_write, txt

    def _process_notification(self, entry):
        """ Cherry picks information from a Kano World notification
            based on its type and returns it in a dict.

            :param entry: A notification entry from the World API
            :returns: A dict that can be passed to the notification widget
        """

        MINECRAFT_SHARE_IMG = media_dir + \
            '/images/notification/280x170/share-pong.png'
        PONG_SHARE_IMG = media_dir + \
            '/images/notification/280x170/share-minecraft.png'
        SP_IMG = media_dir + \
            '/images/notification/280x170/saturday-project.png'
        FOLLOWER_IMG = media_dir + \
            '/images/notification/280x170/follower.png'
        GENERIC_ALERT_IMG = media_dir + \
            '/images/notification/280x170/notification.png'

        n = {
            'id': entry['id'],
            'title': 'Kano World',
            'byline': '',
            'image': GENERIC_ALERT_IMG,
            'command': 'kano-world-launcher /notifications/open/{}'.format(
                       entry['id'])
        }

        # Customise settings for known types
        if entry['category'] == 'follows':
            n['title'] = 'New follower!'
            n['byline'] = entry['title']
            n['image'] = FOLLOWER_IMG

            # Link to whomever followed this user
            user = self._get_dict_value(entry, ['meta', 'author', 'username'])
            if user:
                n['command'] = "kano-world-launcher /users/{}".format(user)

        elif entry['category'] in ['share-items', 'shares']:
            n['title'] = 'New share!'
            n['byline'] = entry['title']

            if entry['type'] == 'make-minecraft':
                n['image'] = MINECRAFT_SHARE_IMG
            elif entry['type'] == 'make-pong':
                n['image'] = PONG_SHARE_IMG

            # Link to the share
            share_id = self._get_dict_value(entry, ['meta', 'item', 'id'])
            if share_id:
                n['command'] = "kano-world-launcher /shared/{}".format(
                    share_id)

        elif entry['category'] == 'comments':
            n['title'] = 'New comment!'
            n['byline'] = entry['title']

            slug = self._get_dict_value(entry, ['meta', 'item', 'slug'])
            if slug:
                obj_type = entry['meta']['item']['type']
                if obj_type == "app":
                    n['command'] = "kano-world-launcher /apps/{}".format(slug)
                elif obj_type == "share":
                    n['command'] = "kano-world-launcher /shared/{}".format(
                        slug)
                elif obj_type == "project":
                    n['command'] = "kano-world-launcher /projects/{}".format(
                        slug)

        # If a notification has both the title and text, override the default
        if 'title' in entry and entry['title'] and \
                'text' in entry and entry['text']:
            n['title'] = entry['title']
            n['byline'] = entry['text']

        # Some notifications may have images
        # If so, we need to download them and resize
        if 'image_url' in entry and entry['image_url']:
            filename = os.path.basename(entry['image_url'])

            img_path = "{}/notifications/{}".format(profile_dir, filename)
            ensure_dir(os.path.dirname(img_path))

            rv, e = download_url(entry['image_url'], img_path)
            if rv:
                # Resize image to 280x170
                # FIXME: We import GdkPixbuf locally to make sure not to
                # bugger up anything else, but we should move it up to the top.
                from gi.repository import GdkPixbuf

                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    img_path, 280, 170)
                pixbuf.savev(img_path, 'png', [None], [None])

                n['image'] = img_path
            else:
                msg = "Notifications image failed to download ({}).".format(e)
                logger.error(msg)

        # Certain notifications may come with a command as well.
        # If so, override the default one.
        cmd = self._get_dict_value(entry, ['meta', 'cmd'])
        if cmd:
            n['command'] = cmd

        return n

    def _get_dict_value(self, root, elements):
        cur_root = root
        for el in elements:
            if type(cur_root) == dict and el in cur_root:
                cur_root = cur_root[el]
            else:
                return None

        return cur_root
