# share_helpers.py
#
# Copyright (C) 2016-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2


from kano.utils.shell import run_cmd

from .functions import login_using_token
from .share import upload_share


def login_and_share(file_path, title, app_name):
    """ Make a share to Kano World. If the user is not logged in, present the
    register/login window to the user.

    :param file_path: Code file to be uploaded to Kano World
    :type file_path: str

    :param title: Title for the share
    :type title: str

    :param app_name: App making the share
    :type app_name: str

    :returns: Success, error message or None
    :rtype: Tuple of (bool, str)
    """
    success, unused = login_using_token()

    if not success:
        run_cmd('kano-login -r', localised=True)
        success, unused = login_using_token()
        if not success:
            return False, _("Cannot login")

    return upload_share(file_path, title, app_name)
