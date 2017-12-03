#
# test_tracking_imports.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Unit tests to ensure that the tracking module exports the
# interface that its users are expecting.
#


import pytest


@pytest.mark.parametrize('module_export', [
    'open_locked',
    'load_token',
    'generate_tracker_token',
    'OS_VERSION',
    'OS_VERSION',
    'CPU_ID',
    'TOKEN',
    'LANGUAGE',
    'get_session_file_path',
    'get_session_unique_id',
    'session_start',
    'session_end',
    'session_log',
    'track_data',
    'track_action',
    'track_subprocess',
    'get_action_event',
    'get_session_event',
    'get_utc_offset',
    'Tracker',
    'add_runtime_to_app',
    'save_hardware_info',
    'save_kano_version',
    'get_tracker_events',
    'clear_tracker_events',
    ])
def test_tracker_module_import(module_export):
    import kano_profile.tracker as tracker

    getattr(tracker, module_export)


@pytest.mark.parametrize('module_export', [
    'generate_event',
    ])
def test_tracking_events_module_import(module_export):
    import kano_profile.tracking_events as tracking_events

    getattr(tracking_events, module_export)
