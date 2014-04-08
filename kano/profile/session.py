#!/usr/bin/env python

import requests
import json
import os
import sys

api_url = 'http://localhost:1234'
content_type_json = {'content-type': 'application/json'}


def read_file_contents(path):
    if os.path.exists(path):
        with open(path) as infile:
            return infile.read().strip()


class ApiSession(object):
    session = requests.Session()

    def __init__(self, token):
        self.session.headers.update({'Authorization': token})
        if not self.test_auth():
            print 'Error with login'

    def test_auth(self):
        r = self.session.get(api_url + '/auth/is-authenticated')
        return r.ok


def create_user(email, username, password):
    payload = {
        'email': email,
        'username': username,
        'password': password
    }
    r = requests.post(api_url + '/users', data=json.dumps(payload), headers=content_type_json)
    return r.ok, r.text


def load_token():
    return read_file_contents('token')


def save_token(str):
    with open('token', 'w') as outfile:
        outfile.write(str)


def login(email, password):
        payload = {
            'email': email,
            'password': password
        }
        r = requests.post(api_url + '/auth', data=json.dumps(payload), headers=content_type_json)

        # return error
        if not r.ok:
            return r.ok, r.text

        # save token and update session
        return r.ok, r.json()['session']['token']


if __name__ == '__main__':
    email = 'zsolt.ero+4@gmail.com'
    username = 'zsero3'
    password = 'passwd'

    # Create user if not found
    registered = True
    if not registered:
        success, error = create_user(email=email, username=username, password=password)
        if not success:
            sys.exit(error)
        else:
            print 'User: {} created'.format(username)
            registered = True

    # load tokan
    token = load_token()

    # login using token
    if token:
        s = ApiSession(token)

    # login using password and save token
    else:
        success, value = login(email=email, password=password)
        if not success:
            print 'Cannot log in, problem: {}'.format(value)
        else:
            token = value
            save_token(token)
            s = ApiSession(token)

