#!/usr/bin/env python

import time
import atexit
from kano.utils import get_program_name
from kano_profile.apps import load_app_state_variable, save_app_state_variable


class Tracker:
    def __init__(self):
        self.start_time = time.time()
        self.program_name = get_program_name()
        atexit.register(add_runtime_to_app, self.program_name, self.calculate_elapsed())

    def calculate_elapsed(self):
        return time.time() - self.start_time


def add_runtime_to_app(app, runtime):
    state = load_app_state_variable('tracker', app)

    if not state or not 'counter' in state:
        state = {
            'counter': 0,
            'runtime': 0,
        }

    # increase variables
    state['counter'] += 1
    state['runtime'] += runtime

    save_app_state_variable('tracker', app, state)






