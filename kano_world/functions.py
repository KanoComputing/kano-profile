# functions.py
#
# Copyright (C) 2014-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Refer to the Network API documentation:
# https://github.com/KanoComputing/kano-web-api/wiki/API-accounts


import json

from kano.logging import logger
from kano_profile.profile import load_profile, save_profile
from kano.utils import get_user_unsudoed
from kano_world.config import load_conf

from .connection import request_wrapper, content_type_json
from .session import KanoWorldSession


glob_session = None
http_verbose = False
kw_url = load_conf()['api_url']


def login(login_name, password, verbose=http_verbose):
    import mercury  # Lazy import to avoid dynamically linking with global import

    login_name = login_name.strip()
    password = password.strip()

    kw = mercury.KanoWorld(kw_url)
    success = kw.login(login_name, password, verbose)
    if success:
        # TODO: refactor function login_register_data
        return True, None
    else:
        return False, _("Could not login to Kano World Services")


def register(email, username, password, marketing_enabled=False):
    email = email.strip()
    username = username.strip()
    password = password.strip()

    payload = {
        'email': email,
        'username': username,
        'password': password,
        'marketing_enabled_primary': str(marketing_enabled).lower()
    }

    success, text, data = request_wrapper('post', '/users', data=json.dumps(payload), headers=content_type_json)
    if success:
        return login_register_data(data)
    else:
        return False, _("Cannot register, problem: {}").format(text)


def set_login_data(id, username, email, token):
    """ Reverse Engineered Wrapper:
    Simulates a "payload" JSON dictionary using the login and register data
    from the WEB API (Qt Interface). Invoked from kano-webengine.

    Args:
        id (str): numerical ID of the user
        username (str): user name
        email (str): user email
        token (str): a unique login/registration token

    Exception:
        Error if unable to login

    Returns:
        bool: True for successful login [through the kano-login backend]
    """

    data = {
        'session': {
            'token': token,
            'user': {
                'username': username,
                'email': email,
                'id': id
            },
        },
        'success': True  # data are only sent from the WEB API on successful login
    }

    try:
        return login_register_data(data)
    except Exception as e:
        logger.error("Error with data from the WEB API: {}".format(e))


def login_register_data(data):
    global glob_session

    profile = load_profile()

    profile['token'] = data['session']['token']
    profile['kanoworld_username'] = data['session']['user']['username']
    profile['kanoworld_id'] = data['session']['user']['id']
    profile['email'] = data['session']['user']['email']

    # We know this field will be returned from the API even if it is empty
    # However we only need to store it if it has a meaningful value
    try:
        if data['session']['user']['secondary_email']:
            profile['secondary_email'] = data['session']['user']['secondary_email']
    except:
        profile.pop('secondary_email', None)

    save_profile(profile)
    try:
        glob_session = KanoWorldSession(profile['token'])
        return True, None
    except Exception as e:
        return False, _("We cannot reach the Kano server. Try again in a few minutes. Error = {}").format(str(e))


def is_registered():
    import mercury  # Lazy import to avoid dynamically linking with global import
    kw = mercury.KanoWorld(kw_url)
    return kw.is_logged_in()


def has_token():
    import mercury  # Lazy import to avoid dynamically linking with global import
    kw = mercury.KanoWorld(kw_url)
    return bool(kw.get_token())


def remove_token():
    profile = load_profile()
    profile.pop('token', None)
    save_profile(profile)


def remove_registration(verbose=http_verbose):
    import mercury  # Lazy import to avoid dynamically linking with global import
    kw = mercury.KanoWorld(kw_url)
    return kw.logout()


def login_using_token():
    if is_registered():
        return True, None
    return False, _("User is not logged in")


def sync():
    if not glob_session:
        return False, _("You are not logged in!")

    success, value = glob_session.upload_profile_stats()
    if not success:
        return False, value

    success, value = glob_session.upload_private_data()
    if not success:
        return False, value

    success, value = glob_session.refresh_notifications()
    if not success:
        return False, value

    success, value = glob_session.upload_tracking_data()
    if not success:
        return False, value

    success, value = glob_session.download_online_badges()
    if not success:
        return False, value

    return True, None


def backup_content(file_path):
    if not glob_session:
        return False, _("You are not logged in!")

    return glob_session.backup_content(file_path)


def restore_content(file_path):
    if not glob_session:
        return False, _("You are not logged in!")

    return glob_session.restore_content(file_path)


def upload_tracking_data():
    if not glob_session:
        return False, _("You are not logged in!")

    success, value = glob_session.upload_tracking_data()
    if not success:
        return False, value

    return True, None


def get_glob_session():
    return glob_session


def get_mixed_username():
    if is_registered():
        import mercury  # Lazy import to avoid dynamically linking with global import
        kw = mercury.KanoWorld(kw_url)
        username = kw.get_username()
    else:
        username = get_user_unsudoed()
    return username


def get_token():
    import mercury  # Lazy import to avoid dynamically linking with global import
    kw = mercury.KanoWorld(kw_url)
    return kw.get_token()


def get_email():
    try:
        email = load_profile()['email']
    except Exception:
        email = ''
    return email


def get_secondary_email():
    try:
        sec_email = load_profile()['secondary_email']
    except Exception:
        sec_email = ''
    return sec_email


def get_kano_world_id():
    try:
        kw_id = load_profile()['kanoworld_id']
    except Exception:
        kw_id = ''
    return kw_id


def recover_username(email):
    payload = {
        'email': email
    }

    success, text, _ = request_wrapper('post', '/accounts/username-reminder',
                                       data=json.dumps(payload),
                                       headers=content_type_json)

    if success:
        return success, None
    else:
        return success, text


def reset_password(username):
    payload = {
        'username': username
    }

    success, text, _ = request_wrapper('post', '/accounts/reset-password',
                                       data=json.dumps(payload),
                                       headers=content_type_json)

    if success:
        return success, None
    else:
        return success, text


def mark_notification_read(n_id):
    if not glob_session:
        return False, _("You are not logged in!")

    success, text, data = request_wrapper(
        'post',
        '/notifications/read/{}'.format(n_id),
        session=glob_session.session
    )

    return success, text


def get_stats_activity():
    # Instantiate the global session variable
    success, text = login_using_token()

    if not success:
        return False, text

    success, text, data = request_wrapper('get', '/stats/activity',
                                          headers=content_type_json,
                                          session=glob_session.session)
    return success, data


def report_share_opened(item_id):
    success, value = login_using_token()
    if success:
        endpoint = '/share/{}/launched'.format(item_id)
        gs = get_glob_session()
        if gs:
            success, text, data = request_wrapper('post',
                                                  endpoint,
                                                  session=gs.session)
