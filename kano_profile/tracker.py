#!/usr/bin/env python

# tracker.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

"""
Kano-tracker module

A small module for tracking various metrics the users do in Kano OS
"""

import time
import atexit
import datetime
from kano.utils import get_program_name, is_number, read_file_contents
from kano_profile.apps import load_app_state_variable, save_app_state_variable


class Tracker:
    """Tracker class, used for measuring program run-times,
    implemented via atexit hooks"""

    def __init__(self):
        self.start_time = time.time()
        self.program_name = get_program_name()
        atexit.register(self.write_times)

    def calculate_elapsed(self):
        return time.time() - self.start_time

    def write_times(self):
        add_runtime_to_app(self.program_name, self.calculate_elapsed())


def add_runtime_to_app(app, runtime):
    """Appends a time period to a given app's runtime stats,
    + raises starts by one"""

    if not app or app == 'kano-tracker':
        return

    if not is_number(runtime):
        return

    runtime = float(runtime)

    app = app.replace('.', '_')

    app_stats = load_app_state_variable('kano-tracker', 'app_stats')
    if not app_stats:
        app_stats = dict()

    try:
        app_stats[app]['starts'] += 1
        app_stats[app]['runtime'] += runtime
    except Exception:
        app_stats[app] = {
            'starts': 1,
            'runtime': runtime,
        }

    save_app_state_variable('kano-tracker', 'app_stats', app_stats)


def save_hardware_info():
    """Saves hardware information related to the Raspberry Pi / Kano Kit"""

    from kano.logging import logger
    from kano.utils import get_cpu_id, get_mac_address, detect_kano_keyboard

    logger.info('save_hardware_info')
    state = {
        'cpu_id': get_cpu_id(),
        'mac_address': get_mac_address(),
        'kano_keyboard': detect_kano_keyboard(),
    }
    save_app_state_variable('kano-tracker', 'hardware_info', state)


def save_kano_version():
    """Saves a dict of os-version: time values,
    to keep track of the users update process"""

    updates = load_app_state_variable('kano-tracker', 'versions')
    if not updates:
        updates = dict()

    version_now = read_file_contents('/etc/kanux_version')
    if not version_now:
        return

    version_now = version_now.replace('.', '_')

    time_now = datetime.datetime.utcnow().isoformat()
    updates[version_now] = time_now

    save_app_state_variable('kano-tracker', 'versions', updates)



