#!/usr/bin/env python

import requests
import json

api_url = 'http://localhost:1234'
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


def create_user(email, username, password):
    payload = {
        'email': email,
        'username': username,
        'password': password
    }
    try:
        r = requests.post(api_url + '/users', data=json.dumps(payload), headers=content_type_json)
        # return ok and error
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
                return r.ok, r.json()['session']['token']
            else:
                # return error
                return r.ok, r.text

        except requests.exceptions.ConnectionError:
            return False, "Connection error"



