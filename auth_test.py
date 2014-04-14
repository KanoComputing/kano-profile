#!/usr/bin/env python

import sys
from kano.world import register_profile, login_profile, \
    is_registered, is_logged_in


if __name__ == '__main__':
    email = '9@abc.com'
    username = '9abc'
    password = 'passwd'

    session = None

    # login or register of id not in profile
    if not is_registered():
        answer = raw_input('Register or login? [r/l]: ')
        if answer.lower() == 'r':
            success, text = register_profile(email, username, password)
            if not success:
                sys.exit(text)
        elif answer.lower() == 'l':
            success, text = login_profile(email, password)
            if not success:
                sys.exit(text)

    if is_logged_in():
        try:
            # session = KanoWorldSession(profile['token'])
            pass
        except Exception:
            success, text = login_profile(email, password)
            if not success:
                sys.exit(text)

    if not session:
        sys.exit('Something really really strange is happening... :-(')

    session.upload_profile_stats()
    session.upload_private_data()
