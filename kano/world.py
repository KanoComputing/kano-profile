#!/usr/bin/env python

import requests
import json

from kano.utils import get_date_now
from kano.profile.profile import load_profile, save_profile
from kano.profile.badges import calculate_xp
from kano.profile.apps import get_app_list, load_app_state, save_app_state

# api_url = 'http://localhost:1234'
# api_url = 'http://10.0.2.2:1234'
api_url = 'http://10.0.1.91:1234'
content_type_json = {'content-type': 'application/json'}

apps_private = ['kano-settings', 'test']
glob_session = None


def request_wrapper(method, endpoint, data=None, headers=None, session=None):
    if method not in ['put', 'get', 'post', 'delete']:
        return False, 'Wrong method name!'

    if session:
        req_object = session
    else:
        req_object = requests

    method = getattr(req_object, method)

    try:
        r = method(api_url + endpoint, data=data, headers=headers)
        if r.ok:
            return r.ok, None, r.json()
        else:
            return r.ok, r.text, None
    except requests.exceptions.ConnectionError:
        return False, 'Connection error', None


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
                data = data['user']

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


def login(email, password):
    global glob_session

    payload = {
        'email': email,
        'password': password
    }

    success, text, data = request_wrapper('post', '/auth', json.dumps(payload), content_type_json)
    if success:
        profile = load_profile()
        profile['token'] = data['session']['token']
        profile['kanoworld_username'] = data['session']['user']['username']
        profile['kanoworld_id'] = data['session']['user']['id']
        profile['email'] = email
        save_profile(profile)
        try:
            glob_session = KanoWorldSession(profile['token'])
            return True, None
        except Exception:
            return False, 'There may be a problem with our servers.  Try again later.'
    else:
        return False, 'Cannot log in, problem: {}'.format(text)


def register_profile(email, username, password):
    payload = {
        'email': email,
        'username': username,
        'password': password
    }

    success, text, data = request_wrapper('post', '/users', json.dumps(payload), content_type_json)
    if success:
        profile = load_profile()
        profile['kanoworld_username'] = data['user']['username']
        profile['kanoworld_id'] = data['user']['id']
        profile['email'] = email
        save_profile(profile)
        return True, email
    else:
        return False, text


def is_registered():
    return 'kanoworld_id' in load_profile()


def has_token():
    return 'token' in load_profile()


def remove_token():
    profile = load_profile()
    profile.pop('token', None)
    save_profile(profile)


def login_test():
    global glob_session

    if not is_registered():
        return False, 'Not registered!'
    if not has_token():
        return False, 'No token!'

    try:
        profile = load_profile()
        glob_session = KanoWorldSession(profile['token'])
        return True, None
    except Exception:
        return False, Exception.text


def sync():
    if not glob_session:
        return False, 'You are not logged in!'

    success, value = glob_session.upload_profile_stats()
    if not success:
        return False, value

    success, value = glob_session.upload_private_data()
    if not success:
        return False, value

    return True, None



