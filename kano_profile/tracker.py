#!/usr/bin/env python

# tracker.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

"""
Kano-tracker module

A small module for tracking various metrics the users do in Kano OS
"""

import time
import atexit
import datetime
import fcntl
import json
import os
import hashlib

from kano.utils import get_program_name, is_number, read_file_contents, \
    get_cpu_id, chown_path, ensure_dir
from kano.logging import logger
from kano_profile.apps import get_app_state_file, load_app_state_variable, \
    save_app_state_variable
from kano_profile.paths import tracker_dir, tracker_events_file, \
    tracker_token_file


class open_locked:
    """ A version of open with an exclusive lock to be used within
        controlled execution statements.
    """

    def __init__(self, path, mode):
        self._fd = open(path, mode)
        fcntl.flock(self._fd, fcntl.LOCK_EX)

    def __enter__(self):
        return self._fd

    def __exit__(self, exit_type, value, traceback):
        self._fd.close()


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
        with open_locked(tracker_token_file, "r") as f:
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
    with open_locked(tracker_token_file, "w") as f:
        f.write(token)

    # Make sure that the events file exist
    open(tracker_events_file, 'a').close()

    return token


OS_VERSION = str(read_file_contents('/etc/kanux_version'))
CPU_ID = str(get_cpu_id())
TOKEN = load_token()


def get_session_file_path(name, pid):
    return "{}/{}-{}.json".format(tracker_dir, pid, name)

def session_start(name, pid=None):
    if not pid:
        pid = os.getpid()
    pid = int(pid)

    data = {
        "pid": pid,
        "name": name,
        "started": int(time.time()),
        "elapsed": 0,
        "finished": False
    }

    path = get_session_file_path(data['name'], data['pid'])

    with open_locked(path, "w") as f:
        json.dump(data, f)
    chown_path(path)

    return path


def session_end(session_file):
    if not os.path.exists(session_file):
        msg = "Someone removed the tracker file, the runtime of this " + \
            "app will not be logged"
        logger.warn(msg)
        return

    with open_locked(session_file, "r") as rf:
        data = json.load(rf)

        data["elapsed"] = int(time.time()) - data["started"]
        data["finished"] = True

        with open(session_file, "w") as wf:
            json.dump(data, wf)


def session_log(name, started, length):
    """ Log a session that was tracked outside of the tracker.

        :param name: The identifier of the session.
        :type name: str

        :param started: When was the session started (UTC unix timestamp).
        :type started: int

        :param length: Length of the session in seconds.
        :param started: int
    """

    with open_locked(tracker_events_file, 'a') as af:
        session = {
            "name": name,
            "started": int(started),
            "elapsed": int(length)
        }

        event = get_session_event(session)
        af.write(json.dumps(event) + "\n")


def track_data(name, data):
    """ Track arbitrary data.

        Calling this function will generate a data tracking event.

        :param name: The identifier of the data.
        :type name: str

        :param data: Arbitrary data, must be compatible with JSON.
        :type data: dict, list, str, int, float, None
    """

    event = {
        "type": "data",
        "time": time.time(),
        "timezone_offset": get_utc_offset(),
        "os_version": OS_VERSION,
        "cpu_id": CPU_ID,
        "token": TOKEN,

        "name": str(name),
        "data": data
    }

    with open_locked(tracker_events_file, "a") as af:
        af.write(json.dumps(event) + "\n")


def track_action(name):
    """ Trigger an action tracking event.

        :param name: The identifier of the action.
        :type name: str
    """

    with open_locked(tracker_events_file, 'a') as af:
        event = get_action_event(name)
        af.write(json.dumps(event) + "\n")


def get_action_event(name):
    return {
        "type": "action",
        "time": int(time.time()),
        "timezone_offset": get_utc_offset(),
        "os_version": OS_VERSION,
        "cpu_id": CPU_ID,
        "token": TOKEN,

        "name": name
    }


def get_session_event(session):
    """ Construct the event data structure for a session. """

    return {
        "type": "session",
        "time": session['started'],
        "timezone_offset": get_utc_offset(),
        "os_version": OS_VERSION,
        "cpu_id": CPU_ID,
        "token": TOKEN,

        "name": session['name'],
        "length": session['elapsed'],
    }


def get_utc_offset():
    """ Returns the local UTC offset in seconds.

        :returns: UTC offsed in secconds.
        :rtype: int
    """

    is_dst = time.daylight and time.localtime().tm_isdst > 0
    return -int(time.altzone if is_dst else time.timezone)

class Tracker:
    """Tracker class, used for measuring program run-times,
    implemented via atexit hooks"""

    def __init__(self):
        self.path = session_start(get_program_name())
        atexit.register(self._write_times)

    def _write_times(self):
        session_end(self.path)


# TODO: While it isn't at the moment, this could be useful to have
#       in the toolset.
def _get_nearest_previous_monday():
    """ Returns the timestamp of the nearest past Monday """

    t = time.time()
    day = 24 * 60 * 60
    week = 7 * day

    r = (t - (t % week)) - (3 * day)
    if (t - r) >= week:
        r += week

    return int(r)


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
    tracker_store = open(app_state_file, "r")
    fcntl.flock(tracker_store, fcntl.LOCK_EX)

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

    week = str(_get_nearest_previous_monday())
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

    with open_locked(tracker_events_file, "r") as rf:
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

    with open_locked(tracker_events_file, "r") as rf:
        events = []
        for event_line in rf.readlines():
            try:
                event = json.loads(event_line)
                if 'token' in event and event['token'] == TOKEN:
                    events.append(event_line)
            except:
                logger.warn("Found a corrupted event, skipping.")

        with open(tracker_events_file, "w") as wf:
            for event_line in events:
                wf.write(event_line)

