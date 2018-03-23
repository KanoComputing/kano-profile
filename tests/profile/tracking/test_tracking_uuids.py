# test_tracking_uuids.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the tracking_uuids module.


import json
from random import randint

from tests.fixtures.tracking import DAY


def test_get_tracking_uuid(tracking_uuids, uuid_key_arg, monkeypatch):
    """Tests :func:`kano_profile.tracker.tracking_uuids.get_tracking_uuid`.

    It checks that existing and not expired UUIDs are retrieved correctly and
    also that non-existent UUIDs are created and stored correctly.
    """

    import kano_profile.tracker.tracking_uuids as m

    time_now = 0

    def mock_time():
        return time_now

    def mock__new_tracking_uuid(key, dummy):
        """Mock function to return a UUID with a given key from UUID_ENTRIES"""
        return tracking_uuids['all_uuids'][key]

    # When the test retrieves an existing UUID entry, mock the time to
    # simulate the UUID still being valid.
    if uuid_key_arg in tracking_uuids['data']:
        time_now = randint(
            tracking_uuids['data'][uuid_key_arg]['timestamp'],
            tracking_uuids['data'][uuid_key_arg]['expires']
        )
        monkeypatch.setattr(m.time, 'time', mock_time)

    # Otherwise, mock the creation function to return one we know of.
    else:
        monkeypatch.setattr(m, '_new_tracking_uuid', mock__new_tracking_uuid)

    expected_tracking_uuid = tracking_uuids['data'].get(
        uuid_key_arg,
        mock__new_tracking_uuid(uuid_key_arg, 0)
    )
    tracking_uuid = m.get_tracking_uuid(uuid_key_arg)

    assert(
        tracking_uuid == expected_tracking_uuid and
        uuid_key_arg in tracking_uuids['fake_file'].contents  # The new UUID is stored
    )


def test_get_tracking_uuid_expired(tracking_uuids, uuid_key_arg, monkeypatch):
    """Tests :func:`kano_profile.tracker.tracking_uuids.get_tracking_uuid`.

    It checks that existing expired UUIDs are retrieved, created again, and
    stored correctly. Also checks that non-existent UUIDs are created and
    stored correctly.
    """

    import kano_profile.tracker.tracking_uuids as m

    time_now = 0

    def mock_time():
        return time_now

    def mock__new_tracking_uuid(key, dummy):
        """Mock function to return a UUID with a given key from UUID_ENTRIES
        with an updated timestamp."""
        tracking_uuid = tracking_uuids['all_uuids'][key]
        tracking_uuid['timestamp'] = time_now
        tracking_uuid['expires'] = time_now + 3 * DAY
        return tracking_uuid

    # When the test retrieves an existing UUID entry, mock the time to
    # simulate the UUID being expired.
    if uuid_key_arg in tracking_uuids['data']:
        time_now = tracking_uuids['data'][uuid_key_arg]['expires'] + 1
        monkeypatch.setattr(m.time, 'time', mock_time)

    # Mock the creation function to return one we know of.
    monkeypatch.setattr(m, '_new_tracking_uuid', mock__new_tracking_uuid)

    expected_tracking_uuid = tracking_uuids['data'].get(
        uuid_key_arg,
        mock__new_tracking_uuid(uuid_key_arg, 0)
    )
    tracking_uuid = m.get_tracking_uuid(uuid_key_arg)

    assert(
        tracking_uuid == expected_tracking_uuid and
        uuid_key_arg in tracking_uuids['fake_file'].contents  # The new UUID is stored
    )


def test_remove_tracking_uuid(tracking_uuids, uuid_key_arg):
    """Tests :func:`kano_profile.tracker.tracking_uuids.remove_tracking_uuid`.

    It checks that any UUID associated with the ``uuid_key_arg`` is removed
    from the file.
    """

    import kano_profile.tracker.tracking_uuids as m
    m.remove_tracking_uuid(uuid_key_arg)

    # Read the fake file back and load the json data.
    data = json.loads(tracking_uuids['fake_file'].contents)

    assert uuid_key_arg not in data


def test__new_tracking_uuid(monkeypatch):
    """Tests :func:`kano_profile.tracker.tracking_uuids._new_tracking_uuid`.

    It checks that the function creates a new UUID object as expected.
    """

    import kano_profile.tracker.tracking_uuids as m

    expected_tracking_uuid = {
        'uuid': 'ceb9aede-bc11-5b2e-a9ab-91b1705cfd2f',
        'timestamp': 10,
        'expires': 20
    }

    def mock_time():
        return expected_tracking_uuid['timestamp']

    def mock_uuid5(namespace, name):
        return expected_tracking_uuid['uuid']

    monkeypatch.setattr(m.time, 'time', mock_time)
    monkeypatch.setattr(m, 'uuid5', mock_uuid5)

    tracking_uuid = m._new_tracking_uuid(
        'test',
        expected_tracking_uuid['expires'] - expected_tracking_uuid['timestamp']
    )

    assert tracking_uuid == expected_tracking_uuid


def test__is_uuid_expired(tracking_uuids, uuid_key_arg, monkeypatch):
    """Tests :func:`kano_profile.tracker.tracking_uuids._is_uuid_expired`.

    It checks that a given UUID object is considered expired correctly.
    """

    import kano_profile.tracker.tracking_uuids as m

    time_now = 0

    def mock_time():
        return time_now

    if uuid_key_arg in tracking_uuids['data']:
        monkeypatch.setattr(m.time, 'time', mock_time)
        tracking_uuid = tracking_uuids['data'][uuid_key_arg]

        time_now = tracking_uuid['expires'] - 1
        less_than_expires = m._is_uuid_expired(tracking_uuid)

        time_now = tracking_uuid['expires']
        equals_expires = m._is_uuid_expired(tracking_uuid)

        time_now = tracking_uuid['expires'] + 1
        greater_than_expires = m._is_uuid_expired(tracking_uuid)

        assert(
            less_than_expires is False and
            equals_expires is False and
            greater_than_expires is True
        )

    # Always consider an empty UUID as expired.
    else:
        assert m._is_uuid_expired(dict()) is True


def test__read_tracking_uuid(tracking_uuids, uuid_key_arg):
    """Tests :func:`kano_profile.tracker.tracking_uuids._read_tracking_uuid`.

    It checks that any UUID associated with the ``uuid_key_arg`` is correctly
    retrieved from the file. If one isn't found, an empty ``dict`` is expected.
    """

    import kano_profile.tracker.tracking_uuids as m

    tracking_uuid = m._read_tracking_uuid(uuid_key_arg)
    expected_tracking_uuid = tracking_uuids['data'].get(uuid_key_arg, dict())

    assert tracking_uuid == expected_tracking_uuid


def test__add_tracking_uuid(tracking_uuids, uuid_key_arg):
    """Tests :func:`kano_profile.tracker.tracking_uuids._add_tracking_uuid`.

    It checks that a given UUID is added correctly to the file. This could be
    either adding or overwriting an existing UUID.
    """

    import kano_profile.tracker.tracking_uuids as m

    expected_tracking_uuid = tracking_uuids['all_uuids'][uuid_key_arg]

    m._add_tracking_uuid(uuid_key_arg, expected_tracking_uuid)

    # Read the fake file back, load the json data, and get the UUID.
    tracking_uuid = json.loads(tracking_uuids['fake_file'].contents)[uuid_key_arg]

    assert tracking_uuid == expected_tracking_uuid


def test__open_uuids(tracking_uuids):
    """Tests :func:`kano_profile.tracker.tracking_uuids._open_uuids`.

    It checks that the function correctly opens the ``tracking_uuids`` file and
    loads the JSON data within.
    """

    import kano_profile.tracker.tracking_uuids as m
    uuids_file, data = m._open_uuids()

    assert uuids_file is not None and data == tracking_uuids['data']
