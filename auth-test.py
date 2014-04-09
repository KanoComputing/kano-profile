#!/usr/bin/env python

import sys
from kano.world import create_user, load_token, ApiSession, login, save_token
from kano.profile import load_profile, save_profile

if __name__ == '__main__':
    email = 'zsolt.ero+4@gmail.com'
    username = 'zsero3'
    password = 'passwd'

    # TODO replace with profile
    # Create user if not found
    registered = True
    if not registered:
        success, error = create_user(email=email, username=username, password=password)
        if not success:
            sys.exit(error)
        else:
            print 'User: {} created'.format(username)
            registered = True

    # load tokan
    token = load_token()

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
            save_token(token)
            try:
                s = ApiSession(token)
            except Exception:
                sys.exit('Cannot log in with fresh token')

