#! /usr/bin/env python

# webapi.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import requests

from urlparse import urljoin
from requests.compat import json


class Error(Exception):
    pass


class AuthError(Error):
    pass


class VersionError(Error):
    pass


class ClientError(Error):
    pass


class ServerError(Error):
    pass


class Client():
    API_HOST = 'https://api.kano.me'
    API_VERSION = '0.0'

    def __init__(self):
        self._session = requests.session()

        if 'KANO_API_HOST' in os.environ:
            self.API_HOST = os.environ['KANO_API_HOST']

    def _request(self, method, endpoint, api_version, **kwargs):
        if not api_version:
            api_version = self.API_VERSION

        url = urljoin(self.API_HOST, endpoint)

        headers = kwargs.pop('headers', {})
        headers.update({
            'Accept': 'application/vnd.kano+json; version={}'.format(api_version)
        })

        action = getattr(self._session, method)
        response = action(url, headers=headers, **kwargs)

        try:
            response.raise_for_status()
        except requests.HTTPError:
            error = response.text
            try:
                error = json.loads(error)
            except (KeyError, ValueError):
                pass

            if response.status_code in (401, 403):
                raise AuthError(error)
            elif response.status_code in (406, 410):
                raise VersionError(error)
            elif response.status_code >= 400 and response.status_code < 500:
                raise ClientError(error)
            elif response.status_code >= 500:
                raise ServerError(error)
            else:
                raise Error(error)

        return response

    def get(self, endpoint, api_version=None, **kwargs):
        return self._request('get', endpoint, api_version, **kwargs)

    def post(self, endpoint, api_version=None, **kwargs):
        return self._request('post', endpoint, api_version, **kwargs)
