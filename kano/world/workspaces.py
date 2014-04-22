#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from .connection import request_wrapper, content_type_json


def list_workspaces(app_name):
    payload = {
        'app_name': app_name
    }

    success, text, data = request_wrapper('get', '/workspaces', headers=content_type_json, params=payload)
    if not success:
        return False, text

    if 'entries' in data and data['entries']:
        return True, data['entries']

    return False, 'Something wrong with getting workspaces!'





