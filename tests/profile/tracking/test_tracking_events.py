#
# test_tracking_events.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Unit tests for functions related to tracking events:
#     `kano_profile.tracker.tracking_events`
#


import os
import json
import time
import pytest

from kano_profile.paths import tracker_events_file
import kano_profile.tracker.tracking_events as tracking_events
from kano_profile.tracker.tracker_token import TOKEN


@pytest.mark.parametrize('event_name, event_type, event_data', [
    ('low-battery', 'battery', '{"status": "low-charge"}'),
    ('auto-poweroff', 'battery', '{"status": "automatic-poweroff"}')
    ])
def test_generate_low_battery_event(event_name, event_type, event_data):
    if os.path.exists(tracker_events_file):
        os.remove(tracker_events_file)

    tracking_events.generate_event(event_name)

    assert os.path.exists(tracker_events_file)

    events = []

    with open(tracker_events_file, 'r') as events_f:
        events.append(json.loads(events_f.readline()))

    assert len(events) == 1

    event = events[0]

    expected_keys = [
        'name',
        'language',
        'type',
        'timezone_offset',
        'cpu_id',
        'os_version',
        'token',
        'time',
        'data'
    ]

    for key in expected_keys:
        assert key in event

    assert event['name'] == event_type
    # language: en_GB,
    assert event['type'] == 'data'
    # timezone_offset: 3600,
    # cpu_id: None,
    # os_version: None,
    assert event['token'] == TOKEN
    # Allow some margin for time passing
    assert abs(time.time() - event['time']) < 5
    assert event['data'] == json.loads(event_data)
