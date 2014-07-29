#!/usr/bin/env python

import time
import sys
import os
import atexit
from kano_profile.apps import load_app_state_variable, save_app_state_variable


def get_program_name():
    program_name = os.path.basename(sys.argv[0])
    return program_name


def print_elapsed():
    print 'print_elapsed'
    delta_time = time.time() - start_time
    print '{}: {}'.format(program_name, delta_time)
    add_runtime_to_app(program_name, delta_time)


def add_runtime_to_app(app, runtime):
    state = load_app_state_variable('tracker', program_name)

    if not state or not 'counter' in state:
        state = {
            'counter': 0,
            'runtime': 0,
        }

    # increase variables
    state['counter'] += 1
    state['runtime'] += runtime

    save_app_state_variable('tracker', program_name, state)


start_time = time.time()
program_name = get_program_name()

atexit.register(print_elapsed)
