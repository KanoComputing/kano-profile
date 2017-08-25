import os
import time
import hashlib
import re

from kano_profile.paths import tracker_token_file
from kano_profile.tracker.tracker_token import load_token, TOKEN, \
    generate_tracker_token


TOKEN_REGEX = re.compile(r'[0-9a-f]{32}')


def validate_token(token):
    assert len(token) == 32
    assert TOKEN_REGEX.match(token)


'''
TODO: Try to do something smarter here as TOKEN is created on import which may
      be invalidated with the manipulations from the other tests
'''
def test_token_var():
    token = load_token()

    assert token == TOKEN
    validate_token(token)


def test_token_cache_load():
    test_token = hashlib.md5(str(time.time())).hexdigest()

    with open(tracker_token_file, 'w') as token_f:
        token_f.write(test_token)

    assert test_token == load_token()


def test_token_regen_load():
    if os.path.exists(tracker_token_file):
        os.remove(tracker_token_file)

    created_token = load_token()

    with open(tracker_token_file, 'r') as token_f:
        expected_token = token_f.read()

    assert created_token == expected_token
    validate_token(created_token)


def test_token_gen():
    if os.path.exists(tracker_token_file):
        os.remove(tracker_token_file)

    created_token = generate_tracker_token()

    with open(tracker_token_file, 'r') as token_f:
        expected_token = token_f.read()

    assert created_token == expected_token
    validate_token(created_token)