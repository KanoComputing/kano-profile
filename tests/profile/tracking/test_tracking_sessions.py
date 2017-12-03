#
# test_tracking_sessions.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Unit tests of session tracking functions:
#     `kano_profile.tracker.tracking_sessions`
#


import os
import json
import pytest

from tests.conftest import sample_tracking_sessions

from kano_profile.paths import tracker_dir


def test_list_sessions(tracking_session, sample_tracking_sessions):
    import kano_profile.tracker.tracking_sessions as tracking_sessions

    tracking_session.setup_sessions(sample_tracking_sessions)
    tracking_session.setup_paused_sessions(None)

    listed_sessions = tracking_sessions.list_sessions()

    assert len(listed_sessions) == len(sample_tracking_sessions)

    for session in sample_tracking_sessions:
        session_path = tracking_sessions.get_session_file_path(
            session['name'],
            session['pid']
        )
        assert os.path.basename(session_path) in listed_sessions


def test_get_open_sessions(tracking_session, sample_tracking_sessions):
    import kano_profile.tracker.tracking_sessions as tracking_sessions

    sample_sessions = sample_tracking_sessions[:]
    open_session = tracking_session.format_session(
        'active-session', 987654321, os.getpid(), 55, True
    )
    sample_sessions.append(open_session)
    tracking_session.setup_sessions(sample_sessions)
    tracking_session.setup_paused_sessions(None)

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
    import kano_profile.tracker.tracking_sessions as tracking_sessions

    session_file_path = os.path.abspath(
        tracking_sessions.get_session_file_path(name, pid)
    )
    assert session_file_path == expected


# TODO: Populate this test
# @pytest.mark.parametrize('name, pid', TEST_DATA)
# def test_get_session_unique_id(name, pid):
#     pass


def test_session_start_with_pid(tracking_session):
    import kano_profile.tracker.tracking_sessions as tracking_sessions
    from kano_profile.tracker.tracking_session import TrackingSession

    tracking_session.setup_sessions([])
    tracking_session.setup_paused_sessions(None)

    test_session = TrackingSession(name='test', pid=1234)
    session_path = tracking_sessions.session_start(
        test_session.name, test_session.pid
    )

    assert os.path.abspath(session_path) == test_session.path

    with open(test_session.path, 'r') as test_session_f:
        session_data = json.load(test_session_f)

    assert test_session.name == session_data['name']
    assert test_session.pid == session_data['pid']


def test_session_start_no_pid(tracking_session):
    import kano_profile.tracker.tracking_sessions as tracking_sessions
    from kano_profile.tracker.tracking_session import TrackingSession

    tracking_session.setup_sessions([])
    tracking_session.setup_paused_sessions(None)

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


def test_get_paused_sessions(tracking_session, sample_tracking_sessions):
    import kano_profile.tracker.tracking_sessions as tracking_sessions
    from kano_profile.tracker.tracking_session import TrackingSession

    tracking_session.setup_paused_sessions(sample_tracking_sessions)

    paused_sessions = tracking_sessions.get_paused_sessions()

    assert len(paused_sessions) == len(sample_tracking_sessions)

    for session in sample_tracking_sessions:
        session_obj = TrackingSession(name=session['name'], pid=session['pid'])
        assert session_obj in paused_sessions


@pytest.mark.parametrize(
    'unpaused_sessions, paused_sessions, expected',
    [
        (sample_tracking_sessions(), [], True),
        (sample_tracking_sessions(), None, False),
        ([], sample_tracking_sessions(), True),
    ]
)
def test_is_tracking_paused(tracking_session, unpaused_sessions, paused_sessions, expected):
    import kano_profile.tracker.tracking_sessions as tracking_sessions

    tracking_session.setup_sessions(unpaused_sessions)
    tracking_session.setup_paused_sessions(paused_sessions)

    assert tracking_sessions.is_tracking_paused() == expected


def test_pause_tracking_sessions(tracking_session, sample_tracking_sessions):
    import kano_profile.tracker.tracking_sessions as tracking_sessions
    from kano_profile.tracker.tracking_session import TrackingSession
    from kano_profile.paths import PAUSED_SESSIONS_FILE

    open_session = tracking_session.format_session(
        'active-session', 987654321, os.getpid(), 55, False
    )
    open_session_obj = TrackingSession(
        name=open_session['name'], pid=open_session['pid']
    )
    sample_tracking_sessions.append(open_session)
    tracking_session.setup_sessions(sample_tracking_sessions)
    tracking_session.setup_paused_sessions(None)

    assert tracking_sessions.get_open_sessions() == [open_session_obj]
    assert tracking_sessions.get_paused_sessions() == []

    tracking_sessions.pause_tracking_sessions()

    assert tracking_sessions.get_open_sessions() == []
    assert tracking_sessions.get_paused_sessions() == [open_session_obj]

    with open(PAUSED_SESSIONS_FILE, 'r') as paused_sessions_f:
        tracking_session = [
            line for line in paused_sessions_f
            if line
        ]
        assert len(tracking_session) == 1
        assert TrackingSession.loads(tracking_session[0]) == open_session_obj


def test_unpause_tracking_sessions(tracking_session, sample_tracking_sessions):
    import kano_profile.tracker.tracking_sessions as tracking_sessions
    from kano_profile.tracker.tracking_session import TrackingSession
    from kano_profile.paths import tracker_dir

    sample_sessions = sample_tracking_sessions[:]
    open_session = tracking_session.format_session(
        'active-session', 987654321, os.getpid(), 55, False
    )
    open_session_obj = TrackingSession(
        name=open_session['name'], pid=open_session['pid']
    )
    sample_sessions.append(open_session)
    tracking_session.setup_sessions([])
    tracking_session.setup_paused_sessions(sample_sessions)

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
    import kano_profile.tracker.tracking_sessions as tracking_sessions
    from kano_profile.paths import tracker_events_file

    if os.path.exists(tracker_events_file):
        os.remove(tracker_events_file)

    tracking_sessions.session_log(name, started, length)

    with open(tracker_events_file, 'r') as events_f:
        events_data = json.load(events_f)

    assert events_data['name'] == name
    assert events_data['time'] == started
    assert events_data['length'] == length
