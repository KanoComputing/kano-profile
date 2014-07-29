#!/usr/bin/env python

import time
import signal
import sys
import os
from kano_profile.apps import increment_app_state_variable


def get_program_name():
    program_name = os.path.basename(sys.argv[0])
    return program_name


def catch_signal(*args):
    print 'catch_signal'
    print_elapsed()
    sys.exit(0)


def print_elapsed():
    print 'print_elapsed'
    delta_time = time.time() - start_time
    print '{}: {}'.format(program_name, delta_time)
    add_runtime_to_app(program_name, delta_time)


def add_runtime_to_app(app, runtime):
    increment_app_state_variable('tracker', program_name, runtime)


start_time = time.time()
program_name = get_program_name()

signal.signal(signal.SIGINT, catch_signal)
signal.signal(signal.SIGTERM, catch_signal)
