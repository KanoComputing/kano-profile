#!/usr/bin/env python

import sys
from kano.world import KanoWorldSession, register_profile, login_profile, \
    is_registered, is_logged_in
from kano.profile.profile import load_profile


if __name__ == '__main__':
    email = '9@abc.com'
    username = '9abc'
    password = 'passwd'

    profile = load_profile()
    session = None

    # login or register of id not in profile
    if not is_registered():
        answer = raw_input('Register or login? [r/l]: ')
        if answer.lower() == 'r':
            success, text = register_profile(email, username, password, profile)
            if not success:
                sys.exit(text)
        elif answer.lower() == 'l':
            success, text, session = login_profile(email, password, profile)
            if not success:
                sys.exit(text)

    if is_logged_in():
        try:
            session = KanoWorldSession(profile['token'])
        except Exception:
            success, text, session = login_profile(email, password, profile)
            if not success:
                sys.exit(text)

    if not session:
        sys.exit('Something really really strange is happening... :-(')

    session.upload_profile_stats()
    session.upload_private_data()
