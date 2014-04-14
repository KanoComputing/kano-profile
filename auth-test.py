#!/usr/bin/env python

import sys
from kano.world import create_user, KanoWorldSession, login
from kano.profile.profile import load_profile, save_profile


def do_login(email, password):
    global profile, s

    success, value = login(email=email, password=password)
    if success:
        profile['token'] = value['session']['token']
        profile['kanoworld_username'] = value['session']['user']['username']
        profile['kanoworld_id'] = value['session']['user']['id']
        profile['email'] = email
        save_profile(profile)
        try:
            s = KanoWorldSession(profile['token'])
        except Exception:
            sys.exit('Cannot log in with fresh token')
    else:
        sys.exit('Cannot log in, problem: {}'.format(value))


def do_register(email, username, password):
    global profile

    success, value = create_user(email=email, username=username, password=password)
    if success:
        print 'User: {} created'.format(username)
        profile['kanoworld_username'] = value['user']['username']
        profile['kanoworld_id'] = value['user']['id']
        profile['email'] = email
        save_profile(profile)
    else:
        sys.exit(value)


if __name__ == '__main__':
    email = '9@abc.com'
    username = '9abc'
    password = 'passwd'

    profile = load_profile()
    s = None

    # login or register of id not in profile
    if 'kanoworld_id' not in profile:
        answer = raw_input('Register or login? [r/l]: ')
        if answer.lower() == 'r':
            do_register(email, username, password)
        elif answer.lower() == 'l':
            do_login(email, password)

    if 'token' in profile:
        try:
            s = KanoWorldSession(profile['token'])
        except Exception:
            do_login(email, password)

    if not s:
        sys.exit('Something really really strange is happening... :-(')

    s.upload_all_stats()


