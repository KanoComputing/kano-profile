#
# test_login.py
#
# Copyright (C) 2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Login tests for the new Kano World Services API, using the Mercury library.
# These tests should be run on a Kano OS RaspberryPI Kit.
#

from kano_world.functions import login

def test_login_failed():
    s, m = login('abcde', '12345')
    assert s is False
    assert type(m) is str
    assert len(m) > 0

def test_login_success():
    s, m = login('testing_user', 'kano12345experience')
    assert s is True
    assert m is None
