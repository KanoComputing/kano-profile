import os
import pytest

from kano_profile.paths import tracker_dir
from kano_profile.tracker.tracking_session import TrackingSession


TEST_DATA = [
    {
        'file': '1242-test-file-1.json',
        'path': os.path.join(tracker_dir, '1242-test-file-1.json'),
        'pid': 1242,
        'name': 'test-file-1'
    },
]


@pytest.mark.parametrize('test_data', TEST_DATA)
def test_file_init(test_data):
    session_file = test_data['file']
    session_path = test_data['path']
    session_pid = test_data['pid']
    session_name = test_data['name']

    session = TrackingSession(session_file=session_file)

    assert session.file == session_file
    assert session.path == session_path
    assert session.pid == session_pid
    assert session.name == session_name


@pytest.mark.parametrize('test_data', TEST_DATA)
def test_pid_name_init(test_data):
    session_file = test_data['file']
    session_path = test_data['path']
    session_pid = test_data['pid']
    session_name = test_data['name']

    session = TrackingSession(pid=session_pid, name=session_name)

    assert session.file == session_file
    assert session.path == session_path
    assert session.pid == session_pid
    assert session.name == session_name
