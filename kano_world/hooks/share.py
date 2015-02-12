#!/usr/bin/env python

# share.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# args is an array of arguments that were passed through the URL
# e.g., kano:share:12345:weee, it will be ["12345", "weee"]

import os
import sys

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano.utils import run_cmd
from kano.logging import logger
from kano_world.share import download_share, get_share_by_id
from kano_profile.apps import launch_project
from kdesk.hourglass import hourglass_start, hourglass_end
from kano_world.connection import request_wrapper
from kano_world.functions import get_glob_session, login_using_token

def run(args):
    try:
        share_id = args[0]
    except Exception:
        return

    # Start an hourglass with an unspecified app,
    # remove it as soon as we have a download resolution
    hourglass_start("")

    success, text, share = get_share_by_id(share_id)
    if not success:
        msg = 'Error downloading share: {}'.format(text)
        logger.error(msg)
        hourglass_end()
        return

    success, data = download_share(share)
    if not success:
        msg = 'Could not download share, error: {}'.format(data)
        logger.error(msg)
        hourglass_end()
        return

    data.append(share_id)
    hourglass_end()
    return data


def launch(data):
    (title, attachment_path, app, attachment_name, folder, item_id) = data
    msg = 'Downloaded share: {}'.format(title)
    logger.info(msg)

    cmd = 'kano-dialog title="Download completed successfully" buttons=Launch:green:1,Return:grey:2'
    _, _, rc = run_cmd(cmd)
    if rc == 1:
        launch_project(app, attachment_name, folder)
        _report_share_opened(item_id)

def _report_share_opened(item_id):
    success, value = login_using_token()
            if success:
                endpoint = '/share/{}/installed'.format(item_id)
                gs = get_glob_session()
                if gs:
                    success, text, data = request_wrapper('post', endpoint,
                                                          session=gs.session)
