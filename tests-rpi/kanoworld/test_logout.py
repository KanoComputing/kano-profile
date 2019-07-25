#
# test_logout.py
#
# Copyright (C) 2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Test the logout functionality.
# These tests should be run on a Kano OS RaspberryPI Kit.
#

from kano_world.functions import login, login_using_token, remove_registration

def test_login_and_logout():
    s, m = login('testing_user', 'kano12345experience')
    assert s is True
    assert m is None

    s, m = login_using_token()
    assert m is None
    assert s is True

    s = remove_registration()
    assert s is True

    s, m = login_using_token()
    assert m is not None
    assert len(m) > 0
    assert s is False
