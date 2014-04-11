#!/usr/bin/env python

import requests
import json

from kano.utils import get_date_now
from kano.profile.profile import load_profile
from kano.profile.badges import calculate_xp
from kano.profile.apps import get_app_list, load_app_state

api_url = 'http://localhost:1234'
# api_url = 'http://10.0.2.2:1234'
content_type_json = {'content-type': 'application/json'}


class ApiSession(object):
    session = requests.Session()

    def __init__(self, token):
        self.session.headers.update({'Authorization': token})
        success, value = self.test_auth()
        if not success:
            raise Exception(value)

    def test_auth(self):
        try:
            r = self.session.get(api_url + '/auth/is-authenticated')
            if r.ok:
                return r.ok, 'OK'
            else:
                # return error
                return r.ok, r.text
        except requests.exceptions.ConnectionError:
            return False, "Connection error"

    def upload_all_stats(self):
        profile = load_profile()

        data = dict()
        for k, v in profile.iteritems():
            if k in ['save_date', 'username_linux', 'mac_addr', 'cpu_id']:
                data[k] = v

        data['xp'] = calculate_xp()
        data['upload_date'] = get_date_now()

        stats = dict()
        for app in get_app_list():
            stats[app] = load_app_state(app)
        data['stats'] = stats
        print data

        r = self.session.put(api_url + '/users/profile', data=json.dumps(data))
        print r.text


# functions not part of ApiSession

def create_user(email, username, password):
    payload = {
        'email': email,
        'username': username,
        'password': password
    }
    try:
        r = requests.post(api_url + '/users', data=json.dumps(payload), headers=content_type_json)
        if r.ok:
            return r.ok, r.json()
        else:
            return r.ok, r.text
    except requests.exceptions.ConnectionError:
        return False, "Connection error"


def login(email, password):
        payload = {
            'email': email,
            'password': password
        }
        try:
            r = requests.post(api_url + '/auth', data=json.dumps(payload), headers=content_type_json)
            if r.ok:
                # return token
                return r.ok, r.json()
            else:
                # return error
                return r.ok, r.text
        except requests.exceptions.ConnectionError:
            return False, "Connection error"



