#
# tracking.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Definition of fixtures for tracking tests
#


import os
import json
from uuid import uuid1, uuid5
import pytest


class TrackingSessionFixture(object):
    @staticmethod
    def format_session(name, started, pid, elapsed, finished):
        return {
            "name": name,
            "started": started,
            "pid": pid,
            "elapsed": elapsed,
            "finished": finished,
            "app_session_id": str(uuid5(uuid1(), '{}{}'.format(name, pid)))
        }

    @classmethod
    def setup_session_fixtures(cls, directory, sessions):
        from kano.utils.file_operations import ensure_dir
        from kano_profile.tracker.tracking_session import TrackingSession

        ensure_dir(directory)
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


    @classmethod
    def setup_sessions(cls, sessions):
        from kano_profile.paths import tracker_dir
        cls.setup_session_fixtures(tracker_dir, sessions)


    @classmethod
    def setup_paused_sessions(cls, sessions):
        from kano_profile.paths import PAUSED_SESSIONS_FILE
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


@pytest.fixture(scope='function')
def sample_tracking_sessions():
    return [
        TrackingSessionFixture.format_session(
            'test-1', 12345678, 1234, 60, True
        ),
        TrackingSessionFixture.format_session(
            'test-2', 22345678, 1234, 32, True
        ),
        TrackingSessionFixture.format_session(
            'test-3', 32345678, 1234, 288, True
        ),
        TrackingSessionFixture.format_session(
            'test-4', 42345678, 1234, 119, False
        ),
        TrackingSessionFixture.format_session(
            'test-5', 52345678, 1234, 3, False
        ),
    ]


@pytest.fixture(scope='module')
def tracking_session():
    return TrackingSessionFixture()


@pytest.fixture(scope='module')
def tracking_session_file_data():
    from kano_profile.paths import tracker_dir

    return {
        'file': '1242-test-file-1.json',
        'path': os.path.join(tracker_dir, '1242-test-file-1.json'),
        'pid': 1242,
        'name': 'test-file-1'
    }
