#
# environment.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Environment setup for feature tests
#


import os


def before_scenario(context, scenario):
    from kano_profile.paths import tracker_dir

    # Clear out tracking sessions
    for path, dirs, files in os.walk(tracker_dir):
        for tracker_f in files:
            os.remove(os.path.join(path, tracker_f))
