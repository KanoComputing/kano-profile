#!/usr/bin/env python

import sys
from kano.world import create_user, ApiSession, login
from kano.profile import load_profile, save_profile

if __name__ == '__main__':
    email = 'zsolt.ero+6@gmail.com'
    username = 'zsero6'
    password = 'passwd'

    profile = load_profile()

    # Create user if not found
    if 'registered' not in profile or profile['registered'] is False:
        success, error = create_user(email=email, username=username, password=password)
        if not success:
            sys.exit(error)
        else:
            print 'User: {} created'.format(username)
            profile['registered'] = True
            save_profile(profile)

    # load tokan
    token = None
    if 'token' in profile and profile['token']:
        token = profile['token']

    # login using token
    need_login = False
    if token:
        try:
            s = ApiSession(token)
        except Exception:
            need_login = True

    # login using password and save token
    if not token or need_login:
        success, value = login(email=email, password=password)
        if not success:
            print 'Cannot log in, problem: {}'.format(value)
        else:
            token = value
            profile['token'] = token
            save_profile(profile)
            try:
                s = ApiSession(token)
            except Exception:
                sys.exit('Cannot log in with fresh token')

