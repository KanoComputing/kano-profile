#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import requests
import json
import os

from kano.utils import download_url, read_json, write_json
from kano.profile.profile import load_profile, set_avatar, set_environment
from kano.profile.badges import calculate_xp
from kano.profile.apps import get_app_list, load_app_state, save_app_state
from kano.profile.paths import app_profiles_file

from .connection import request_wrapper, content_type_json

app_profiles_data = read_json(app_profiles_file)


def is_private(app_name):
    private = False
    if app_name in app_profiles_data and 'private' in app_profiles_data[app_name]:
        private = app_profiles_data[app_name]['private']
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

        # xp, TODO will be removed
        data['xp'] = calculate_xp()

        # age
        try:
            data['age'] = profile['age']
        except Exception:
            pass

        # gender
        try:
            gender = profile['gender']
            if gender == 'Boy':
                gender = 'm'
            elif gender == 'Girl':
                gender = 'f'
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

        # # location
        # if 'location' not in profile:
        #     profile['location'] = get_location(False)
        # try:
        #     data['location'] = profile['location']
        # except Exception:
        #     pass

        # app states
        stats = dict()
        for app in get_app_list():
            if not is_private(app):
                stats[app] = load_app_state(app)

        # append stats
        data['stats'] = stats

        # write_json('up.json', data)

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

        # write_json('down.json', data)

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

        if not data:
            return True, None

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

        if 'user_backup' in data and 'file_url' in data['user_backup']:
            file_url = data['user_backup']['file_url']
        else:
            return False, 'file_url not found'

        return download_url(file_url, file_path)

    def upload_share(self, file_path, title, app_name, featured):
        if not os.path.exists(file_path):
            return False, 'File path not found: {}'.format(file_path)

        files = {
            'attachment': open(file_path, 'rb'),
        }

        payload = {
            'title': title,
            'featured': featured
        }

        endpoint = '/share/{}'.format(app_name)

        success, text, data = request_wrapper('post', endpoint, session=self.session, files=files, data=payload)
        if not success:
            return False, text

        success = 'success' in data and data['success']
        if not success:
            return False, 'Backup not successful!'
        return True, None

    def delete_share(self, share_id):
        endpoint = '/share/{}'.format(share_id)

        success, text, data = request_wrapper('delete', endpoint, session=self.session)
        if not success:
            return False, text
        return True, None




