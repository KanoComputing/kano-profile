#
# tracking_utils.py
#
# Copyright (C) 2014 - 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utility functions useful for tracking
#

import fcntl
import time


class open_locked(file):
    """ A version of open with an exclusive lock to be used within
        controlled execution statements.
    """
    def __init__(self, *args, **kwargs):
        super(open_locked, self).__init__(*args, **kwargs)
        fcntl.flock(self, fcntl.LOCK_EX)


# TODO: While it isn't at the moment, this could be useful to have
#       in the toolset.
def _get_nearest_previous_monday():
    """ Returns the timestamp of the nearest past Monday """

    t = time.time()
    day = 24 * 60 * 60
    week = 7 * day

    r = (t - (t % week)) - (3 * day)
    if (t - r) >= week:
        r += week

    return int(r)


def get_utc_offset():
    """ Returns the local UTC offset in seconds.

        :returns: UTC offsed in secconds.
        :rtype: int
    """

    is_dst = time.daylight and time.localtime().tm_isdst > 0
    return -int(time.altzone if is_dst else time.timezone)
