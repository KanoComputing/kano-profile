#!/usr/bin/env python

# session.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import requests
import json
import os

from kano.logging import logger
from kano.utils import download_url, read_json
from kano_profile.profile import load_profile, set_avatar, set_environment, save_profile
from kano_profile.badges import calculate_xp
from kano_profile.apps import get_app_list, load_app_state, save_app_state
from kano_profile.paths import app_profiles_file

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
        try:
            avatar_generator = {
                'character': profile['avatar'],
                'environment': ['all', profile['environment']]
            }
            data['avatar_generator'] = avatar_generator
        except Exception:
            pass

        # app states
        stats = dict()
        for app in get_app_list():
            if not is_private(app):
                stats[app] = load_app_state(app)

        # append stats
        data['stats'] = stats

        success, text, response_data = request_wrapper('put', '/users/profile', data=json.dumps(data), headers=content_type_json, session=self.session)
        if not success:
            return False, text

        return self.download_profile_stats(response_data)

    def download_profile_stats(self, data=None):
        if not data:
            profile = load_profile()
            if 'kanoworld_id' in profile:
                user_id = profile['kanoworld_id']
            else:
                return False, 'Profile not registered!'

            success, text, data = request_wrapper('get', '/users/' + user_id, headers=content_type_json, session=self.session)
            if not success:
                return False, text

        try:
            avatar_subcat, avatar_item = data['user']['avatar']['generator']['character']
            set_avatar(avatar_subcat, avatar_item)

            environment = data['user']['avatar']['generator']['environment'][1]
            set_environment(environment)
        except Exception:
            pass

        # app states
        try:
            app_data = data['user']['profile']['stats']
        except Exception:
            return False, 'Data missing from payload!'

        for app, values in app_data.iteritems():
            if not values or (len(values.keys()) == 1 and 'save_date' in values):
                continue
            if not is_private(app):
                save_app_state(app, values)
        return True, None

    def upload_private_data(self):
        data = dict()
        for app in get_app_list():
            if is_private(app):
                data[app] = load_app_state(app)

        payload = dict()
        payload['data'] = data

        success, text, data = request_wrapper('put', '/sync/data', data=json.dumps(payload), headers=content_type_json, session=self.session)
        if not success:
            return False, text

        return self.download_private_data(data)

    def download_private_data(self, data=None):
        if not data:
            success, text, data = request_wrapper('get', '/sync/data', headers=content_type_json, session=self.session)
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

        files = {'file': open(file_path, 'rb')}

        success, text, data = request_wrapper('put', '/sync/backup', session=self.session, files=files)
        if not success:
            return False, text

        success = 'success' in data and data['success']
        if not success:
            return False, 'Backup not successful!'
        return True, None

    def restore_content(self, file_path):
        success, text, data = request_wrapper('get', '/sync/backup', session=self.session)
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

        # paths
        jsonfile_path = file_path[:-3] + 'json'
        screenshot_path = file_path[:-3] + 'png'
        resource_path = file_path[:-3] + 'tar.gz'

        logger.debug('uploading json: {}'.format(jsonfile_path))

        # attachment
        files = {
            'attachment': open(file_path, 'rb'),
        }

        # screenshot
        if os.path.exists(screenshot_path):
            logger.debug('uploading screenshot: {}'.format(screenshot_path))
            files['cover'] = open(screenshot_path, 'rb')

        # resource
        if os.path.exists(resource_path):
            logger.debug('uploading resource: {}'.format(resource_path))
            files['resource'] = open(resource_path, 'rb')

        # data
        payload = {
            'title': title,
            'featured': featured
        }

        # description
        try:
            description = read_json(jsonfile_path)['description']
            payload['description'] = description
        except Exception:
            description = None

        logger.debug('uploading payload: {}'.format(payload))
        logger.debug('uploading files: {}'.format(files))

        endpoint = '/share/{}'.format(app_name)

        success, text, data = request_wrapper('post', endpoint, session=self.session, files=files, data=payload)
        if not success:
            return False, text

        success = 'success' in data and data['success']
        if not success:
            return False, 'Share upload not successful!'
        return True, None

    def delete_share(self, share_id):
        endpoint = '/share/{}'.format(share_id)

        success, text, data = request_wrapper('delete', endpoint, session=self.session)
        if not success:
            return False, text
        return True, None

    def refresh_notifications(self):
        next_page = 1
        notifications = []
        while next_page is not None:
            success, text, data = request_wrapper(
                'get',
                '/notifications?read=false&page={}'.format(next_page),
                session=self.session
            )

            if not success:
                return False, text

            for entry in data['entries']:
                if entry['read'] is False:
                    n = {
                        'title': 'Kano World',
                        'byline': entry['title'],
                        'image': None,
                        'command': None
                    }
                    notifications.append(n)

            try:
                next_page = data['next']
            except:
                break

        profile = load_profile()
        profile['notifications'] = notifications
        save_profile(profile)
        return True, None
