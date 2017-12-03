#
# test_tracking_session.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Unit tests pertaining to the tracking session class:
#     `kano_profile.tracker.tracking_session`
#


def test_file_init(tracking_session_file_data):
    from kano_profile.tracker.tracking_session import TrackingSession

    session_file = tracking_session_file_data['file']
    session_path = tracking_session_file_data['path']
    session_pid = tracking_session_file_data['pid']
    session_name = tracking_session_file_data['name']

    session = TrackingSession(session_file=session_file)

    assert session.file == session_file
    assert session.path == session_path
    assert session.pid == session_pid
    assert session.name == session_name


def test_pid_name_init(tracking_session_file_data):
    from kano_profile.tracker.tracking_session import TrackingSession

    session_file = tracking_session_file_data['file']
    session_path = tracking_session_file_data['path']
    session_pid = tracking_session_file_data['pid']
    session_name = tracking_session_file_data['name']

    session = TrackingSession(pid=session_pid, name=session_name)

    assert session.file == session_file
    assert session.path == session_path
    assert session.pid == session_pid
    assert session.name == session_name
