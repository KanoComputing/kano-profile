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


def run(args):
    try:
        share_id = args[0]
    except Exception:
        return

    success, text, share = get_share_by_id(share_id)
    if not success:
        msg = 'Error downloading share: {}'.format(text)
        logger.error(msg)
        return

    success, data = download_share(share)
    if not success:
        msg = 'Could not download share, error: {}'.format(data)
        logger.error(msg)
        return

    return data


def launch(data):
    (title, attachment_path, app, attachment_name, folder) = data
    msg = 'Downloaded share: {}'.format(title)
    logger.info(msg)

    cmd = 'kano-dialog title="Download completed successfully" buttons=Launch:green:1,Return:grey:2'
    _, _, rc = run_cmd(cmd)
    if rc == 1:
        launch_project(app, attachment_name, folder)
