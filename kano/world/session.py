#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import requests
import json

from kano.utils import get_date_now
from kano.profile.profile import load_profile
from kano.profile.badges import calculate_xp
from kano.profile.apps import get_app_list, load_app_state, save_app_state

from .connection import request_wrapper, content_type_json


apps_private = ['kano-settings', 'test']


class KanoWorldSession(object):
    session = requests.Session()

    def __init__(self, token):
        self.session.headers.update({'Authorization': token})
        success, text, _ = self.test_auth()
        if not success:
            raise Exception(text)

    def test_auth(self):
        return request_wrapper('get', '/auth/is-authenticated', session=self.session)

    def upload_profile_stats(self):
        profile = load_profile()

        # append profile data
        data = dict()
        for k, v in profile.iteritems():
            if k in ['save_date', 'username_linux', 'mac_addr', 'cpu_id']:
                data[k] = v

        # append xp and upload date
        data['xp'] = calculate_xp()
        data['upload_date'] = get_date_now()

        stats = dict()
        for app in get_app_list():
            if app not in apps_private:
                stats[app] = load_app_state(app)

        # append stats
        data['stats'] = stats

        payload = dict()
        payload['values'] = data

        success, text, data = request_wrapper('put', '/users/profile', json.dumps(payload), content_type_json, session=self.session)
        if not success:
            return False, text
        else:
            return self.download_profile_stats(data)

    def download_profile_stats(self, data=None):
        if not data:
            profile = load_profile()
            if 'kanoworld_id' in profile:
                user_id = profile['kanoworld_id']
            else:
                return False, 'Profile not registered!'

            success, text, data = request_wrapper('get', '/users/' + user_id, content_type_json, session=self.session)
            if not success:
                return False, text
            else:
                if 'user' in data:
                    data = data['user']
                else:
                    return False, 'User field missing from data!'

        if 'profile' in data and 'stats' in data['profile']:
            app_data = data['profile']['stats']
        else:
            return False, 'Data missing from payload!'

        for app, values in app_data.iteritems():
            if not values or (len(values.keys()) == 1 and 'save_date' in values):
                continue
            if app not in apps_private:
                save_app_state(app, values)
        return True, None

    def upload_private_data(self):
        data = dict()
        for app in get_app_list():
            if app in apps_private:
                data[app] = load_app_state(app)

        payload = dict()
        payload['data'] = data

        success, text, data = request_wrapper('put', '/sync/data', json.dumps(payload), content_type_json, session=self.session)
        if not success:
            return False, text
        else:
            return self.download_private_data(data)

    def download_private_data(self, data=None):
        if not data:
            success, text, data = request_wrapper('get', '/sync/data', content_type_json, session=self.session)
            if not success:
                return False, text

        if 'user_data' in data and 'data' in data['user_data']:
            app_data = data['user_data']['data']
        else:
            return False, 'Data missing missing from payload!'

        for app, values in app_data.iteritems():
            if app in apps_private:
                save_app_state(app, values)
        return True, None

