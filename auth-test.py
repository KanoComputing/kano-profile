#!/usr/bin/env python

import sys
from kano.profile.api import create_user, load_token, ApiSession, login, save_token

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
    if token:
        s = ApiSession(token)

    # login using password and save token
    else:
        success, value = login(email=email, password=password)
        if not success:
            print 'Cannot log in, problem: {}'.format(value)
        else:
            token = value
            save_token(token)
            s = ApiSession(token)

