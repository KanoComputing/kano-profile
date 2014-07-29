#!/usr/bin/env python

import time
import atexit
from kano.utils import get_program_name
from kano_profile.apps import load_app_state_variable, save_app_state_variable


class Tracker:
    def __init__(self):
        self.start_time = time.time()
        self.program_name = get_program_name()
        atexit.register(self.write_times)

    def calculate_elapsed(self):
        return time.time() - self.start_time

    def write_times(self):
        add_runtime_to_app(self.program_name, self.calculate_elapsed())


def add_runtime_to_app(app, runtime):
    if not app:
        return

    state = load_app_state_variable('tracker', app)

    try:
        state['starts'] += 1
        state['runtime'] += runtime
    except Exception:
        state = {
            'starts': 1,
            'runtime': runtime,
        }

    save_app_state_variable('tracker', app, state)
