import os
import json
import pytest
from uuid import uuid1, uuid5

import kano_profile.tracker.tracking_sessions as tracking_sessions
from kano_profile.tracker.tracking_session import TrackingSession
from kano_profile.paths import tracker_dir, PAUSED_SESSIONS_FILE, \
    tracker_events_file


'''
{"name": "kano-dashboard", "started": 1459774858, "pid": 9999, "elapsed": 7, "finished": true, "app_session_id": "d1ea40d1-ddc8-5a62-97a2-980b71a9bc19"}
'''

def format_session(name, started, pid, elapsed, finished):
    return {
        "name": name,
        "started": started,
        "pid": pid,
        "elapsed": elapsed,
        "finished": finished,
        "app_session_id": str(uuid5(uuid1(), '{}{}'.format(name, pid)))
    }


def setup_session_fixtures(directory, sessions):
    for session_f in os.listdir(directory):
        session_path = os.path.join(directory, session_f)
        if os.path.isfile(session_path):
            os.remove(session_path)

    for session in sessions:
        session_obj = TrackingSession(
            name=session['name'],
            pid=session['pid']
        )
        session_path = os.path.join(directory, session_obj.file)

        with open(session_path, 'w') as session_f:
            json.dump(session, session_f)


def setup_sessions_dir(sessions):
    setup_session_fixtures(tracker_dir, sessions)

def setup_paused_sessions_file(sessions):
    if sessions == None:
        if os.path.exists(PAUSED_SESSIONS_FILE):
            os.remove(PAUSED_SESSIONS_FILE)

        return

    with open(PAUSED_SESSIONS_FILE, 'w') as sessions_f:
        for session in sessions:
            sessions_f.write(
                '{}\n'.format(json.dumps({
                    'name': session['name'],
                    'pid': session['pid']
                }))
            )


SAMPLE_SESSIONS = [
    format_session('test-1', 12345678, 1234, 60, True),
    format_session('test-2', 22345678, 1234, 32, True),
    format_session('test-3', 32345678, 1234, 288, True),
    format_session('test-4', 42345678, 1234, 119, False),
    format_session('test-5', 52345678, 1234, 3, False),
]


def test_list_sessions():
    setup_sessions_dir(SAMPLE_SESSIONS)
    setup_paused_sessions_file(None)

    listed_sessions = tracking_sessions.list_sessions()

    assert len(listed_sessions) == len(SAMPLE_SESSIONS)

    for session in SAMPLE_SESSIONS:
        session_path = tracking_sessions.get_session_file_path(
            session['name'],
            session['pid']
        )
        assert os.path.basename(session_path) in listed_sessions


def test_get_open_sessions():
    sample_sessions = SAMPLE_SESSIONS[:]
    open_session = format_session(
        'active-session', 987654321, os.getpid(), 55, True
    )
    sample_sessions.append(open_session)
    setup_sessions_dir(sample_sessions)
    setup_paused_sessions_file(None)

    listed_sessions = tracking_sessions.get_open_sessions()

    for session in listed_sessions:
        assert session.is_open()

    assert len(listed_sessions) == 1

    listed_session = listed_sessions[0]

    open_session_path = tracking_sessions.get_session_file_path(
        open_session['name'],
        open_session['pid']
    )

    assert os.path.basename(open_session_path) == listed_session.file
    assert os.path.abspath(open_session_path) == listed_session.path
    assert open_session['name'] == listed_session.name
    assert open_session['pid'] == listed_session.pid


@pytest.mark.parametrize('name, pid, expected', [
    ('test-1', 1234, os.path.join(tracker_dir, '1234-test-1.json')),
    ('test-2', 5830, os.path.join(tracker_dir, '5830-test-2.json')),
])
def test_get_session_file_path(name, pid, expected):
    session_file_path = os.path.abspath(
        tracking_sessions.get_session_file_path(name, pid)
    )
    assert session_file_path == expected


# @pytest.mark.parametrize('name, pid', TEST_DATA)
# def test_get_session_unique_id(name, pid):
#     pass


def test_session_start_with_pid():
    setup_sessions_dir([])
    setup_paused_sessions_file(None)

    test_session = TrackingSession(name='test', pid=1234)
    session_path = tracking_sessions.session_start(
        test_session.name, test_session.pid
    )

    assert os.path.abspath(session_path) == test_session.path

    with open(test_session.path, 'r') as test_session_f:
        session_data = json.load(test_session_f)

    assert test_session.name == session_data['name']
    assert test_session.pid == session_data['pid']


def test_session_start_no_pid():
    setup_sessions_dir([])
    setup_paused_sessions_file(None)

    test_session = TrackingSession(name='test', pid=os.getpid())
    session_path = tracking_sessions.session_start(
        test_session.name
    )

    assert os.path.abspath(session_path) == test_session.path

    with open(test_session.path, 'r') as test_session_f:
        session_data = json.load(test_session_f)

    assert test_session.name == session_data['name']
    assert test_session.pid == session_data['pid']


def test_session_end():
    pass


def test_get_paused_sessions():
    setup_paused_sessions_file(SAMPLE_SESSIONS)

    paused_sessions = tracking_sessions.get_paused_sessions()

    assert len(paused_sessions) == len(SAMPLE_SESSIONS)

    for session in SAMPLE_SESSIONS:
        session_obj = TrackingSession(name=session['name'], pid=session['pid'])
        assert session_obj in paused_sessions


# @pytest.mark.parametrize('session', TEST_DATA)
# def test_pause_tracking_session(session):
#     pass
#
#
# @pytest.mark.parametrize('session', TEST_DATA)
# def test_unpause_tracking_session(session):
#     pass


@pytest.mark.parametrize(
    'unpaused_sessions, paused_sessions, expected',
    [
        (SAMPLE_SESSIONS, [], True),
        (SAMPLE_SESSIONS, None, False),
        ([], SAMPLE_SESSIONS, True),
    ]
)
def test_is_tracking_paused(unpaused_sessions, paused_sessions, expected):
    setup_sessions_dir(unpaused_sessions)
    setup_paused_sessions_file(paused_sessions)

    assert tracking_sessions.is_tracking_paused() == expected


def test_pause_tracking_sessions():
    sample_sessions = SAMPLE_SESSIONS[:]
    open_session = format_session(
        'active-session', 987654321, os.getpid(), 55, False
    )
    open_session_obj = TrackingSession(
        name=open_session['name'], pid=open_session['pid']
    )
    sample_sessions.append(open_session)
    setup_sessions_dir(sample_sessions)
    setup_paused_sessions_file(None)

    assert tracking_sessions.get_open_sessions() == [open_session_obj]
    assert tracking_sessions.get_paused_sessions() == []

    tracking_sessions.pause_tracking_sessions()

    assert tracking_sessions.get_open_sessions() == []
    assert tracking_sessions.get_paused_sessions() == [open_session_obj]

    with open(PAUSED_SESSIONS_FILE, 'r') as paused_sessions_f:
        sessions = [
            line for line in paused_sessions_f
            if line
        ]
        assert len(sessions) == 1
        assert TrackingSession.loads(sessions[0]) == open_session_obj


def test_unpause_tracking_sessions():
    sample_sessions = SAMPLE_SESSIONS[:]
    open_session = format_session(
        'active-session', 987654321, os.getpid(), 55, False
    )
    open_session_obj = TrackingSession(
        name=open_session['name'], pid=open_session['pid']
    )
    sample_sessions.append(open_session)
    setup_sessions_dir([])
    setup_paused_sessions_file(sample_sessions)

    tracking_sessions.unpause_tracking_sessions()

    assert tracking_sessions.get_open_sessions() == [open_session_obj]
    assert tracking_sessions.get_paused_sessions() == []

    for path, dummy_dirs, files in os.walk(tracker_dir):
        if path == tracker_dir:
            assert len(files) == 1
            assert files[0] == open_session_obj.file


@pytest.mark.parametrize(
    'name, started, length',
    [
        ('test-1', 123456, 1337),
    ]
)
def test_session_log(name, started, length):
    if os.path.exists(tracker_events_file):
        os.remove(tracker_events_file)

    tracking_sessions.session_log(name, started, length)

    with open(tracker_events_file, 'r') as events_f:
        events_data = json.load(events_f)

    assert events_data['name'] == name
    assert events_data['time'] == started
    assert events_data['length'] == length
