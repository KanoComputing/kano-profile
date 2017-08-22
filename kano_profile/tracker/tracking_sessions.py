import os
import json
import time
from uuid import uuid1, uuid5

from kano.utils.file_operations import chown_path, ensure_dir
from kano.logging import logger
from kano_profile.tracker.tracker_token import TOKEN
from kano_profile.paths import tracker_dir, tracker_events_file, \
    PAUSED_SESSION_DIR
from kano_profile.tracker.tracking_session import TrackingSession
from kano_profile.tracker.tracking_utils import open_locked


def list_sessions():
    return os.listdir(tracker_dir)


def get_open_sessions():
    open_sessions = []

    for session_file in list_sessions():
        session = TrackingSession(session_file=session_file)

        if not os.path.isfile(session.path):
            continue

        if not session.is_open():
            continue

        open_sessions.append(session)

    return open_sessions


def get_session_file_path(name, pid):
    return "{}/{}-{}.json".format(tracker_dir, pid, name)


def get_session_unique_id(name, pid):
    data = {}
    tracker_session_file = get_session_file_path(name, pid)
    try:
        af = open_locked(tracker_session_file, 'r')
    except (IOError, OSError) as e:
        logger.error("Error while opening session file: {}".format(e))
    else:
        with af:
            try:
                data = json.load(af)
            except ValueError as e:
                logger.error("Session file is not a valid JSON")

    return data.get('app_session_id', "")


def session_start(name, pid=None):
    if not pid:
        pid = os.getpid()
    pid = int(pid)

    data = {
        'pid': pid,
        'name': name,
        'started': int(time.time()),
        'elapsed': 0,
        'app_session_id': str(uuid5(uuid1(), name + str(pid))),
        'finished': False,
        'token-system': TOKEN
    }

    path = get_session_file_path(data['name'], data['pid'])

    try:
        f = open_locked(path, 'w')
    except IOError as e:
        logger.error("Error opening tracker session file {}".format(e))
    else:
        with f:
            json.dump(data, f)
        if 'SUDO_USER' in os.environ:
            chown_path(path)

    return path


def session_end(session_file):
    if not os.path.exists(session_file):
        msg = "Someone removed the tracker file, the runtime of this " \
              "app will not be logged"
        logger.warn(msg)
        return

    try:
        rf = open_locked(session_file, 'r')
    except IOError as e:
        logger.error("Error opening the tracker session file {}".format(e))
    else:
        with rf:
            data = json.load(rf)

            data['elapsed'] = int(time.time()) - data['started']
            data['finished'] = True

            try:
                wf = open(session_file, 'w')
            except IOError as e:
                logger.error(
                    "Error opening the tracker session file {}".format(e))
            else:
                with wf:
                    json.dump(data, wf)
        if 'SUDO_USER' in os.environ:
            chown_path(session_file)


def get_paused_sessions():
    if os.path.exists(PAUSED_SESSION_DIR):
        return [
            TrackingSession(session_file=f)
            for f in os.listdir(PAUSED_SESSION_DIR)
        ]
    else:
        return []


def pause_tracking_session(session):
    '''
    Close session
    Copy session file to tmp

    # shutil.cp(session.path, os.path.join(PAUSED_SESSION_DIR, session.file))
    # session.close()
    # session.rename()
    # mark new sessions for queue
    '''

    print session

    ensure_dir(PAUSED_SESSION_DIR)



def unpause_tracking_session(session):
    '''

    # shutil.cp(PAUSED_SESSION_DIR, session.file), session.path)
    # session.started = now()
    # session.elapsed = 0
    # session.app_sessoin_id = ???

    '''
    print session



def pause_tracking_sessions():
    '''
    '''
    open_sessions = get_open_sessions()

    for session in open_sessions:
        pause_tracking_session(session)


def unpause_tracking_sessions():
    '''
    '''
    for session in get_paused_sessions():
        unpause_tracking_session(session)


def session_log(name, started, length):
    """ Log a session that was tracked outside of the tracker.

        :param name: The identifier of the session.
        :type name: str

        :param started: When was the session started (UTC unix timestamp).
        :type started: int

        :param length: Length of the session in seconds.
        :param started: int
    """

    try:
        af = open_locked(tracker_events_file, 'a')
    except IOError as e:
        logger.error("Error while opening events file: {}".format(e))
    else:
        with af:
            session = {
                'name': name,
                'started': int(started),
                'elapsed': int(length)
            }

            event = get_session_event(session)
            af.write(json.dumps(event) + "\n")
        if 'SUDO_USER' in os.environ:
            chown_path(tracker_events_file)
