#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from .connection import request_wrapper, content_type_json


def list_workspaces(app_name, page):
    payload = {
        'app_name': app_name,
        'page': page,
        'limit': 10
    }

    success, text, data = request_wrapper('get', '/workspaces', headers=content_type_json, params=payload)
    if not success:
        return success, text, None

    if 'entries' in data and data['entries']:
        return True, None, data

    return False, 'Something wrong with getting workspaces!', None





