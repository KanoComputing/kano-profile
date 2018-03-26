# tracking_uuids.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Functions for creating namespaced UUIDs for apps.


import os
import time
import json
from uuid import uuid1, uuid5

from kano.utils.file_operations import chown_path, touch
from kano.logging import logger

from kano_profile.tracker.tracking_utils import open_locked
from kano_profile.paths import TRACKER_UUIDS_PATH


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR


def get_tracking_uuid(key, expires=3 * DAY):
    """Generate or retrieve a namespaced randomised hash string.

    This can be used in situations where certain tracking events require a
    unique ID attached for grouping and timelining. The uuid is associated with
    the given key and stored. If there is no uuid associated with the given key
    a new one will be created, otherwise it will be retrieved from storage.

    Callers of this function are required to use :func:`.remove_tracking_uuid`
    when the uuid is no longer needed. If this is omitted, the hash will expire
    after a certain amount of time and a subsequent call will generate a new one.

    Args:
        key (str): The namespace for the generated uuid to use for retrieval.
        expires (int): Time in seconds from the time of calling this function
            to use as an expiry timestamp. Only used when creating a new uuid.

    Returns:
        dict: A uuid object. See :func:`._new_tracking_uuid`.
    """

    tracking_uuid = _read_tracking_uuid(key)

    if not tracking_uuid or _is_uuid_expired(tracking_uuid):
        tracking_uuid = _new_tracking_uuid(key, expires)
        _add_tracking_uuid(key, tracking_uuid)

    return tracking_uuid


def _new_tracking_uuid(key, expires):
    """Create a new uuid object with the given parameters.

    Args:
        key (str): the `name` used in generating the UUID. See :func:`uuid.uuid5`.
        expires (int): See :func:`.get_tracking_uuid`.

    Returns:
        dict: A uuid object.
    """

    timestamp = time.time()

    return {
        'uuid': str(uuid5(uuid1(), key)),
        'timestamp': timestamp,
        'expires': timestamp + expires
    }


def _is_uuid_expired(tracking_uuid):
    """Check whether a given uuid object is expired.

    Args:
        tracking_uuid (dict): A uuid object.

    Returns:
        bool: Whether the uuid is expired.
    """

    expired = time.time() > tracking_uuid.get('expires', 0)
    logger.debug('tracking_uuid {} expired = {}'.format(tracking_uuid, expired))

    return expired


def _read_tracking_uuid(key):
    """Retrieve the key associated uuid from storage.

    Args:
        key (str): The namespace associated with a uuid, e.g. 'kano-tracker-ctl'.

    Returns:
        dict: A uuid object if one is found or an empty dict otherwise.
    """

    uuids_file, data = _open_uuids()
    uuids_file.close()

    return data.get(key, dict())


def _add_tracking_uuid(key, tracking_uuid):
    """Store a new uuid object.

    Args:
        key (str): The namespace associated with a uuid, e.g. 'kano-tracker-ctl'.
    """

    uuids_file, data = _open_uuids()
    if not uuids_file:
        logger.error('Could not store tracking uuid!')
        return

    with uuids_file:
        data[key] = tracking_uuid
        uuids_file.seek(0)
        uuids_file.truncate(0)
        uuids_file.write(json.dumps(data))

    if 'SUDO_USER' in os.environ:
        chown_path(TRACKER_UUIDS_PATH)


def remove_tracking_uuid(key):
    """Remove the uuid object associated with the given key.

    Args:
        key (str): The namespace associated with a uuid, e.g. 'kano-tracker-ctl'.

    Returns:
        bool: Whether the operation was successful or not.
    """

    uuids_file, data = _open_uuids()
    if not uuids_file:
        return False

    with uuids_file:
        if key in data:
            data.pop(key)
            uuids_file.seek(0)
            uuids_file.truncate(0)
            uuids_file.write(json.dumps(data))

    if 'SUDO_USER' in os.environ:
        chown_path(TRACKER_UUIDS_PATH)

    return True


def _open_uuids():
    """Helper function to open the uuids file and load the JSON inside.

    Returns:
        file, dict: The opened uuids file and its JSON data.
    """

    newly_created = False
    uuids_file = None
    data = dict()

    if not os.path.exists(TRACKER_UUIDS_PATH):
        touch(TRACKER_UUIDS_PATH)
        newly_created = True

    try:
        uuids_file = open_locked(TRACKER_UUIDS_PATH, 'r+')
    except (IOError, OSError) as error:
        logger.error('Error while opening uuids file: {}'.format(error))

    else:
        if newly_created:
            uuids_file.write(json.dumps(data))
            uuids_file.seek(0)

        try:
            data = json.load(uuids_file)
        except ValueError as error:
            logger.error('File uuids does not contain valid JSON: {}'.format(error))

    return uuids_file, data
