#!/usr/bin/env python

# connection.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import requests

# api_url = 'http://10.0.1.91:1234'
api_url = 'https://api.kano.me'

content_type_json = {'content-type': 'application/json'}


def request_wrapper(method, endpoint, data=None, headers=None, session=None, files=None, params=None):
    if method not in ['put', 'get', 'post', 'delete']:
        return False, 'Wrong method name!'

    if session:
        req_object = session
    else:
        req_object = requests

    method = getattr(req_object, method)

    try:
        r = method(api_url + endpoint, data=data, headers=headers, files=files, params=params)
        if r.ok:
            return r.ok, None, r.json()
        else:
            if '<title>Application Error</title>' in r.text:
                error_msg = 'Sorry, our server are having some problems, we are working on getting them back!'
            else:
                error_msg = r.text
            return r.ok, error_msg, None
    except requests.exceptions.ConnectionError as e:
        return False, 'Connection error: {}'.format(str(e)), None
