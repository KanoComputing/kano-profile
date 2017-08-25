import pytest

import kano_profile.tracker as tracker
import kano_profile.tracking_events as tracking_events


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
    getattr(tracker, module_export)


@pytest.mark.parametrize('module_export', [
    'generate_event',
    ])
def test_tracking_events_module_import(module_export):
    getattr(tracking_events, module_export)
