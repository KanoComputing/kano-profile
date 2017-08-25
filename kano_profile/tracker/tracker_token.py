#
# tracker_token.py
#
# Copyright (C) 2014 - 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tracking token manipulation
#

import os
import time
import hashlib

from kano.utils.file_operations import ensure_dir, chown_path
from kano.logging import logger
from kano_profile.paths import tracker_dir, tracker_token_file, \
    tracker_events_file
from kano_profile.tracker.tracking_utils import open_locked


def load_token():
    """
        Reads the tracker token from the token file. If the file doesn't
        exists, it regenerates it.

        The token is regenerated on each boot and is inserted into every
        event to link together events that happened during the same start
        of the OS.

        :returns: The token.
        :rtype: str
    """

    if os.path.exists(tracker_token_file):
        try:
            f = open_locked(tracker_token_file, 'r')
        except IOError as e:
            logger.error("Error opening tracker token file {}".format(e))
        else:
            with f:
                return f.read().strip()
    else:
        return generate_tracker_token()


def generate_tracker_token():
    """
        Generating the token is a simple md5hash of the current time.

        The token is saved to the `tracker_token_file`.

        :returns: The token.
        :rtype: str
    """

    token = hashlib.md5(str(time.time())).hexdigest()

    ensure_dir(tracker_dir)
    try:
        f = open_locked(tracker_token_file, 'w')
    except IOError as e:
        logger.error(
            "Error opening tracker token file (generate) {}".format(e))
    else:
        with f:
            f.write(token)
        if 'SUDO_USER' in os.environ:
            chown_path(tracker_token_file)

    # Make sure that the events file exist
    try:
        f = open(tracker_events_file, 'a')
    except IOError as e:
        logger.error("Error opening tracker events file {}".format(e))
    else:
        f.close()
        if 'SUDO_USER' in os.environ:
            chown_path(tracker_events_file)

    return token


TOKEN = load_token()
