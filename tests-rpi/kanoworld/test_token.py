#
# test_token.py
#
# Copyright (C) 2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Login token tests for the new Kano World Services API, using the Mercury library.
# These tests should be run on a Kano OS RaspberryPI Kit.
#

from kano_world.functions import login, has_token, get_token, login_using_token

def test_login_and_has_token():
    s, m = login('testing_user', 'kano12345experience')
    assert s is True
    assert m is None

    s = has_token()
    assert s is not None
    assert len(s) > 32

    t = get_token()
    assert t is not None
    assert len(t) > 32


def test_login_failed_and_no_token():
    s, m = login('abcde', '12345')
    assert s is False
    assert m is not None

    s = has_token()
    assert s is None

    t = get_token()
    assert t is None
