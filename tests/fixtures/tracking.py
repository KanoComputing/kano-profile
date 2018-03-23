#
# tracking.py
#
# Copyright (C) 2017-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Definition of fixtures for tracking tests
#


import os
import json
from uuid import uuid1, uuid5

import pytest

from tests.utils import all_combinations


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

UUID_KEYS = [
    'kano-updater',
    'terminal-quest',
    'make-snake',
    'story-mode'
]

UUID_ENTRIES = [
    {
        UUID_KEYS[0]: {
            'uuid': 'ceb9aede-bc11-5b2e-a9ab-91b1705cfd2f',
            'timestamp': 1521808547,
            'expires': 1521808547 + 30 * SECOND
        }
    },
    {
        UUID_KEYS[1]: {
            'uuid': '933c68ea-1d94-54d3-90d9-833fef17f3e7',
            'timestamp': 1521808815,
            'expires': 1521808815 + 20 * MINUTE
        }
    },
    {
        UUID_KEYS[2]: {
            'uuid': '69c7bfec-d000-50e6-9ed2-e31686319867',
            'timestamp': 1521808850,
            'expires': 1521808850 + 4 * HOUR
        }
    },
    {
        UUID_KEYS[3]: {
            'uuid': 'baa3c575-7b1a-552d-8564-e1b3230c01b2',
            'timestamp': 1521808873,
            'expires': 1521808873 + 3 * DAY
        }
    }
]

ALL_UUIDS = dict()
for uuid_entry in UUID_ENTRIES:
    key = uuid_entry.keys()[0]
    ALL_UUIDS[key] = uuid_entry[key]


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
        if sessions is None:
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


@pytest.fixture(scope='function', params=(UUID_KEYS))
def uuid_key_arg(request):
    """Fixture parameterised with all mocked UUID keys to test with."""

    return request.param


@pytest.fixture(scope='function', params=all_combinations(UUID_ENTRIES))
def tracking_uuids(request, fs, monkeypatch):
    """Parameterised fixture to setup a number of fake ``uuids`` files.

    This is parameterised with all combinations of UUID_ENTRIES, returning
    everything from ``{}`` data to ``{<all_uuids>}``. When this is combined
    with :func:`.uuid_key_arg` fixture, tests will run against all UUID keys
    times all combinations of UUIDs output to the uuids file.

    Returns:
        dict: With the following fields:
            'fake_file': A :class:`pyfakefs.fake_filesystem.FakeFile` object
                to mock the tracking uuids file.
            'data': A ``dict`` object with the data contained in the fake_file.
            'all_uuids': A ``dict`` object with all mocked the UUID entries.
                This is for when tests require to "get a new one".
    """

    # TODO: Figure out why open_locked is not fooled by pyfakefs and tbk-ing.
    import kano_profile.tracker.tracking_uuids
    monkeypatch.setattr(kano_profile.tracker.tracking_uuids, 'open_locked', open)

    from kano_profile.paths import TRACKER_UUIDS_PATH

    uuids = dict()

    for uuid_entry in request.param:
        uuid_key = uuid_entry.keys()[0]
        uuids[uuid_key] = uuid_entry[uuid_key]

    fake_uuids = fs.CreateFile(TRACKER_UUIDS_PATH, contents=json.dumps(uuids))

    yield {
        'fake_file': fake_uuids,
        'data': uuids,
        'all_uuids': ALL_UUIDS
    }

    # Clean up code, remove the file altogether.
    fs.RemoveFile(TRACKER_UUIDS_PATH)
