#
# test_tracker_token.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Unit tests for functions related to the tracking token:
#     `kano_profile.tracker.tracker_token`
#


import os
import time
import hashlib
import re


TOKEN_REGEX = re.compile(r'[0-9a-f]{32}')


def validate_token(token):
    assert len(token) == 32
    assert TOKEN_REGEX.match(token)


'''
TODO: Try to do something smarter here as TOKEN is created on import which may
      be invalidated with the manipulations from the other tests
'''
def test_token_var():
    from kano_profile.tracker.tracker_token import load_token, TOKEN
    token = load_token()

    assert token == TOKEN
    validate_token(token)


def test_token_cache_load():
    from kano_profile.paths import tracker_token_file
    from kano_profile.tracker.tracker_token import load_token

    test_token = hashlib.md5(str(time.time())).hexdigest()

    with open(tracker_token_file, 'w') as token_f:
        token_f.write(test_token)

    assert test_token == load_token()


def test_token_regen_load():
    from kano_profile.paths import tracker_token_file
    from kano_profile.tracker.tracker_token import load_token

    if os.path.exists(tracker_token_file):
        os.remove(tracker_token_file)

    created_token = load_token()

    with open(tracker_token_file, 'r') as token_f:
        expected_token = token_f.read()

    assert created_token == expected_token
    validate_token(created_token)


def test_token_gen():
    from kano_profile.paths import tracker_token_file
    from kano_profile.tracker.tracker_token import generate_tracker_token

    if os.path.exists(tracker_token_file):
        os.remove(tracker_token_file)

    created_token = generate_tracker_token()

    with open(tracker_token_file, 'r') as token_f:
        expected_token = token_f.read()

    assert created_token == expected_token
    validate_token(created_token)
