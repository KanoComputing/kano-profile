#!/usr/bin/env python

# connection.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import requests
from kano.logging import logger
from kano_world.config import API_URL
from pprint import pformat


content_type_json = {'content-type': 'application/json'}

try:
    from kano_settings.system.proxy import get_requests_proxies
    proxies = get_requests_proxies()
except Exception:
    proxies = None


def _remove_sensitive_data(request_debug):
    if request_debug \
       and 'data' in request_debug \
       and request_debug['data']:

        import ast
        data = ast.literal_eval(str(request_debug['data']))

        if 'password' in data:
            data['password'] = 'removed'
            request_debug['data'] = data

    return request_debug


def request_wrapper(method, endpoint, data=None, headers=None,
                    session=None, files=None, params=None):
    if method not in ['put', 'get', 'post', 'delete']:
        return False, 'Wrong method name!'

    if session:
        req_object = session
    else:
        req_object = requests

    method = getattr(req_object, method)

    request_debug = {
        'url': API_URL + endpoint,
        'data': data,
        'headers': headers,
        'files': files,
        'params': params,
        'proxies': proxies,
    }

    try:
        r = method(API_URL + endpoint, data=data, headers=headers,
                   files=files, params=params, proxies=proxies)
        if r.ok:
            return r.ok, None, r.json()
        else:
            logger.error('error in request to: {}'.format(API_URL + endpoint))
            logger.debug(pformat(_remove_sensitive_data(request_debug)))
            logger.error('response:')
            logger.error(r.text)

            if '<title>Application Error</title>' in r.text:
                error_msg = 'We cannot reach the Kano server. Try again in a few minutes.'
            else:
                error_msg = r.text
            return r.ok, error_msg, None
    except requests.exceptions.ConnectionError as e:
        logger.error('connection error: {}'.format(e))
        logger.debug(pformat(_remove_sensitive_data(request_debug)))

        return False, 'Error connecting to servers, please check your internet connection and try again later.', None



