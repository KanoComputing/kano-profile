#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import requests

api_url = 'http://10.0.1.91:1234'
content_type_json = {'content-type': 'application/json'}


def request_wrapper(method, endpoint, data=None, headers=None, session=None, files=None):
    if method not in ['put', 'get', 'post', 'delete']:
        return False, 'Wrong method name!'

    if session:
        req_object = session
    else:
        req_object = requests

    method = getattr(req_object, method)

    try:
        r = method(api_url + endpoint, data=data, headers=headers, files=files)
        if r.ok:
            return r.ok, None, r.json()
        else:
            return r.ok, r.text, None
    except requests.exceptions.ConnectionError:
        return False, 'Connection error', None
