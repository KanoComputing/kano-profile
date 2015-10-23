# launch.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

# args is an array of arguments that were passed through the URL
# e.g., kano:launch:app-name, it will be ["app-name"]

from kano.logging import logger
from kano_profile.apps import launch_project


def run(args):
    try:
        ret = args[0]
    except (TypeError, IndexError) as exc:
        logger.error(
            "Can't get first element of {} - [{}]".format(str(args), exc)
        )
        ret = None
    return ret


def launch(app_name):
    if app_name is not None:
        try:
            launch_project(app_name, '', '')
        except ValueError:
            logger.error('Failed to launch app "{}"'.format(str(app_name)))
