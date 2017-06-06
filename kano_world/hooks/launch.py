# launch.py
#
# Copyright (C) 2015-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

# args is an array of arguments that were passed through the URL
# e.g., kano:launch:app-name, it will be ["app-name"]

from kano.logging import logger
from kano_profile.apps import launch_project, check_installed


def run(args):
    try:
        ret = args[0]
    except (TypeError, IndexError) as exc:
        logger.error(
            "Can't get first element of {} - [{}]".format(str(args), exc)
        )
        ret = None
    return ret


def launch(app_name, background=False):
    if app_name is not None:
        try:
            if check_installed(app_name):
                launch_project(app_name, '', '', background=background)
        except ValueError:
            logger.error("Failed to launch app '{}'".format(str(app_name)))
