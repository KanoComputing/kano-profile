#
# __init__.py
#
# Copyright (C) 2014 - 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Kano-tracker module
#
# A small module for tracking various metrics the users do in Kano OS
#


__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'


import time
import atexit
import datetime
import fcntl
import json
import os
import hashlib
import subprocess
import shlex

from uuid import uuid1, uuid5

from kano.utils.processes import get_program_name
from kano.utils.file_operations import read_file_contents, chown_path, \
    ensure_dir
from kano.utils.hardware import get_cpu_id
from kano.utils.misc import is_number
from kano.logging import logger
from kano_profile.apps import get_app_state_file, load_app_state_variable, \
    save_app_state_variable
from kano_profile.paths import tracker_dir, tracker_events_file, \
    tracker_token_file

from kano_profile.tracker.tracker_token import TOKEN, generate_tracker_token, \
       load_token
from kano_profile.tracker.tracking_utils import open_locked, \
    get_nearest_previous_monday, get_utc_offset

# Public imports
from kano_profile.tracker.tracker import Tracker
from kano_profile.tracker.tracking_sessions import session_start, session_end, \
    get_session_file_path, session_log, get_session_unique_id, \
    get_session_event, CPU_ID, LANGUAGE, OS_VERSION


def track_data(name, data):
    """ Track arbitrary data.

        Calling this function will generate a data tracking event.

        :param name: The identifier of the data.
        :type name: str

        :param data: Arbitrary data, must be compatible with JSON.
        :type data: dict, list, str, int, float, None
    """

    event = {
        'type': 'data',
        'time': int(time.time()),
        'timezone_offset': get_utc_offset(),
        'os_version': OS_VERSION,
        'cpu_id': CPU_ID,
        'token': TOKEN,
        'language': LANGUAGE,
        'name': str(name),
        'data': data
    }

    try:
        af = open_locked(tracker_events_file, 'a')
    except IOError as e:
        logger.error("Error opening tracker events file {}".format(e))
    else:
        with af:
            af.write(json.dumps(event) + "\n")
        if 'SUDO_USER' in os.environ:
            chown_path(tracker_events_file)


def track_action(name):
    """ Trigger an action tracking event.

        :param name: The identifier of the action.
        :type name: str
    """

    try:
        af = open_locked(tracker_events_file, 'a')
    except IOError as e:
        logger.error("Error opening tracker events file {}".format(e))
    else:
        with af:
            event = get_action_event(name)
            af.write(json.dumps(event) + "\n")
        if 'SUDO_USER' in os.environ:
            chown_path(tracker_events_file)


def track_subprocess(name, cmd):
    """ Launch and track the session of a process.

        :param name: Name of the session.
        :type name: str

        :param cmd: The command line (env vars are not supported).
        :type cmd: str
    """

    cmd_args = shlex.split(cmd)
    p = subprocess.Popen(cmd_args)
    pid = p.pid
    session_start(name, pid)
    p.wait()
    session_end(get_session_file_path(name, pid))


def get_action_event(name):
    return {
        'type': 'action',
        'time': int(time.time()),
        'timezone_offset': get_utc_offset(),
        'os_version': OS_VERSION,
        'cpu_id': CPU_ID,
        'token': TOKEN,
        'language': LANGUAGE,
        'name': name
    }


def add_runtime_to_app(app, runtime):
    """ Saves the tracking data for a given application.

        Appends a time period to a given app's runtime stats and raises
        starts by one. Apart from the total values, it also updates the
        weekly stats.

        This function uses advisory file locks (see flock(2)) to avoid
        races between different applications saving their tracking data
        at the same time.

        :param app: The name of the application.
        :type app: str
        :param runtime: For how long was the app running.
        :type runtime: number
    """

    if not app or app == 'kano-tracker':
        return

    if not is_number(runtime):
        return

    runtime = float(runtime)

    app = app.replace('.', '_')

    # Make sure no one else is accessing this file
    app_state_file = get_app_state_file('kano-tracker')

    try:
        tracker_store = open_locked(app_state_file, 'r')
    except IOError as e:
        logger.error("Error opening app state file {}".format(e))
    else:
        app_stats = load_app_state_variable('kano-tracker', 'app_stats')
        if not app_stats:
            app_stats = dict()

        try:
            app_stats[app]['starts'] += 1
            app_stats[app]['runtime'] += runtime
        except Exception:
            app_stats[app] = {
                'starts': 1,
                'runtime': runtime,
            }

        # Record usage data on per-week basis
        if 'weekly' not in app_stats[app]:
            app_stats[app]['weekly'] = {}

        week = str(get_nearest_previous_monday())
        if week not in app_stats[app]['weekly']:
            app_stats[app]['weekly'][week] = {
                'starts': 0,
                'runtime': 0
            }

        app_stats[app]['weekly'][week]['starts'] += 1
        app_stats[app]['weekly'][week]['runtime'] += runtime

        save_app_state_variable('kano-tracker', 'app_stats', app_stats)

        # Close the lock
        tracker_store.close()


def save_hardware_info():
    """Saves hardware information related to the Raspberry Pi / Kano Kit"""

    from kano.logging import logger
    from kano.utils import get_cpu_id, get_mac_address, detect_kano_keyboard

    logger.info('save_hardware_info')
    state = {
        'cpu_id': get_cpu_id(),
        'mac_address': get_mac_address(),
        'kano_keyboard': detect_kano_keyboard(),
    }
    save_app_state_variable('kano-tracker', 'hardware_info', state)


def save_kano_version():
    """Saves a dict of os-version: time values,
    to keep track of the users update process"""

    updates = load_app_state_variable('kano-tracker', 'versions')
    if not updates:
        updates = dict()

    version_now = read_file_contents('/etc/kanux_version')
    if not version_now:
        return

    version_now = version_now.replace('.', '_')

    time_now = datetime.datetime.utcnow().isoformat()
    updates[version_now] = time_now

    save_app_state_variable('kano-tracker', 'versions', updates)


def get_tracker_events(old_only=False):
    """ Read the events log and return a dictionary with all of them.

        :param old_only: Don't return events from the current boot.
        :type old_only: boolean

        :returns: A dictionary suitable to be sent to the tracker endpoint.
        :rtype: dict
    """

    data = {'events': []}

    try:
        rf = open_locked(tracker_events_file, 'r')
    except IOError as e:
        logger.error("Error opening the tracker events file {}".format(e))
    else:
        with rf:
            for event_line in rf.readlines():
                try:
                    event = json.loads(event_line)
                except:
                    logger.warn("Found a corrupted event, skipping.")

                if _validate_event(event) and event['token'] != TOKEN:
                    data['events'].append(event)

    return data


def _validate_event(event):
    """ Check whether the event is correct so the API won't reject it.

        :param event: The event data.
        :type event: dict

        :returns: True/False
        :rtype: Boolean
    """

    if 'type' not in event:
        return False

    if 'time' not in event or type(event['time']) != int:
        return False

    if 'timezone_offset' not in event or type(event['timezone_offset']) != int:
        return False

    if 'os_version' not in event:
        return False

    if 'cpu_id' not in event:
        return False

    if 'token' not in event:
        return False

    if event['timezone_offset'] < -24*60*60 or \
       event['timezone_offset'] > 24*60*60:
        return False

    return True


def clear_tracker_events(old_only=True):
    """ Truncate the events file, removing all the cached data.

        :param old_only: Don't remove data from the current boot.
        :type old_only: boolean
    """
    try:
        rf = open_locked(tracker_events_file, 'r')
    except IOError as e:
        logger.error("Error opening tracking events file {}".format(e))
    else:
        with rf:
            events = []
            for event_line in rf.readlines():
                try:
                    event = json.loads(event_line)
                    if 'token' in event and event['token'] == TOKEN:
                        events.append(event_line)
                except:
                    logger.warn("Found a corrupted event, skipping.")

            with open(tracker_events_file, 'w') as wf:
                for event_line in events:
                    wf.write(event_line)
            if 'SUDO_USER' in os.environ:
                chown_path(tracker_events_file)
