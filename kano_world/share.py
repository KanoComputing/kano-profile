#!/usr/bin/env python

# share.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from slugify import slugify

from kano.utils import get_home, download_url, ensure_dir, read_json, write_json
from kano_profile.paths import app_profiles_file
from kano.logging import logger
from .connection import request_wrapper, content_type_json
from .functions import get_glob_session, get_kano_world_id


def list_shares(app_name=None, page=0, featured=False, user_id=None):
    payload = {
        'app_name': app_name,
        'page': page,
        'featured': int(featured),
        'limit': 10
    }
    if user_id:
        payload['user_id'] = user_id

    success, text, data = request_wrapper('get', '/share', headers=content_type_json, params=payload)
    if not success:
        return success, text, None

    if 'entries' in data:
        return True, None, data

    return False, 'Something wrong with listing shares!', None


def get_comments(share_id):
    success, text, data = request_wrapper(
        'get', '/comments/share/{}'.format(share_id)
    )

    if not success:
        return success, text, None

    if 'entries' in data:
        return True, None, data['entries']

    return False, 'Something wrong retrieving comments!', None


def post_comment(share_id, comment):
    glob_session = get_glob_session()

    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.post_comment(share_id, comment)


def like_share(share_id):
    glob_session = get_glob_session()

    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.like_share(share_id)


def unlike_share(share_id):
    glob_session = get_glob_session()

    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.unlike_share(share_id)


def get_following():
    glob_session = get_glob_session()

    if not glob_session:
        return False, 'You are not logged in!'

    user_id = get_kano_world_id()
    return glob_session.get_users_following(user_id)


def follow_user(user_id):
    glob_session = get_glob_session()

    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.follow_user(user_id)


def unfollow_user(user_id):
    glob_session = get_glob_session()

    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.unfollow_user(user_id)


def upload_share(file_path, title, app_name, featured=False):
    glob_session = get_glob_session()
    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.upload_share(file_path, title, app_name, featured)


def delete_share(share_id):
    glob_session = get_glob_session()
    if not glob_session:
        return False, 'You are not logged in!'

    return glob_session.delete_share(share_id)


def get_share_by_id(share_id):
    endpoint = '/share/{}'.format(share_id)
    success, text, data = request_wrapper('get', endpoint, headers=content_type_json)
    if not success:
        return success, text, None
    if 'item' in data:
        return success, None, data['item']


def download_share(entry):
    app = entry['app']
    title = entry['title']
    description = entry['description']
    attachment_url = entry['attachment_url']
    cover_url = entry['cover_url']
    resource_url = entry['resource_url']

    data = {
        'title': title,
        'description': description
    }

    app_profiles = read_json(app_profiles_file)

    if app not in app_profiles:
        logger.error('Cannot download share, app not found in app-profiles')
        return

    app_profile = app_profiles[app]

    folder = os.path.join(get_home(), app_profile['dir'], 'webload')
    ensure_dir(folder)

    title_slugified = slugify(title)

    # Download attachment
    attachment_ext = attachment_url.split('.')[-1]
    attachment_name = '{}.{}'.format(title_slugified, attachment_ext)
    attachment_path = os.path.join(folder, attachment_name)

    success, text = download_url(attachment_url, attachment_path)
    if not success:
        msg = 'Error with downloading share file: {}'.format(text)
        logger.error(msg)
        return False, msg

    # Download screenshot
    if cover_url:
        cover_ext = cover_url.split('.')[-1]
        cover_name = '{}.{}'.format(title_slugified, cover_ext)
        cover_path = os.path.join(folder, cover_name)

        success, text = download_url(cover_url, cover_path)
        if not success:
            msg = 'Error with downloading cover file: {}'.format(text)
            logger.error(msg)
            return False, msg

    # Download resource file
    if resource_url:
        resource_ext = resource_url.split('.')[-1]
        # Make sure we don't remove the tar from gz
        if "tar.gz" in resource_url:
            resource_ext = 'tar.' + resource_ext
        resource_name = '{}.{}'.format(title_slugified, resource_ext)
        resource_path = os.path.join(folder, resource_name)

        success, text = download_url(resource_url, resource_path)
        if not success:
            msg = 'Error with downloading resource file: {}'.format(text)
            logger.error(msg)
            return False, msg

    # JSON file
    json_name = '{}.{}'.format(title_slugified, 'json')
    json_path = os.path.join(folder, json_name)
    write_json(json_path, data)
    return True, [title, attachment_path, app, attachment_name, folder]
