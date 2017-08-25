import os
import sys

from kano_profile.paths import tracker_dir


def before_scenario(context, scenario):
    # Clear out tracking sessions
    for path, dirs, files in os.walk(tracker_dir):
        for tracker_f in files:
            os.remove(os.path.join(path, tracker_f))
