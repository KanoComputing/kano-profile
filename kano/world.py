#!/usr/bin/env python

import requests
import json

from kano.utils import get_date_now
from kano.profile.profile import load_profile, save_profile
from kano.profile.badges import calculate_xp
from kano.profile.apps import get_app_list, load_app_state

# api_url = 'http://localhost:1234'
# api_url = 'http://10.0.2.2:1234'
api_url = 'http://10.0.1.91:1234'
content_type_json = {'content-type': 'application/json'}

apps_private = ['kano-settings']


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

        return request_wrapper('put', '/users/profile', json.dumps(payload), content_type_json, session=self.session)

    def upload_private_data(self):
        data = dict()
        for app in get_app_list():
            if app in apps_private:
                data[app] = load_app_state(app)

        payload = dict()
        payload['data'] = data

        return request_wrapper('put', '/sync/data', json.dumps(payload), content_type_json, session=self.session)


def create_user(email, username, password):
    payload = {
        'email': email,
        'username': username,
        'password': password
    }
    return request_wrapper('post', '/users', json.dumps(payload), content_type_json)


def login(email, password):
    payload = {
        'email': email,
        'password': password
    }
    return request_wrapper('post', '/auth', json.dumps(payload), content_type_json)


def login_profile(email, password, profile):
    success, text, data = login(email=email, password=password)
    if success:
        profile['token'] = data['session']['token']
        profile['kanoworld_username'] = data['session']['user']['username']
        profile['kanoworld_id'] = data['session']['user']['id']
        profile['email'] = email
        save_profile(profile)
        try:
            session = KanoWorldSession(profile['token'])
            return True, None, session
        except Exception:
            return False, 'There may be a problem with our servers.  Try again later.', None
    else:
        return False, 'Cannot log in, problem: {}'.format(text), None


def register_profile(email, username, password, profile):
    success, text, data = create_user(email=email, username=username, password=password)
    if success:
        profile['kanoworld_username'] = data['user']['username']
        profile['kanoworld_id'] = data['user']['id']
        profile['email'] = email
        save_profile(profile)
        return True, email
    else:
        return False, text
