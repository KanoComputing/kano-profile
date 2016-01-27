# app_progress_helpers.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Implement higher level progress helpers

from kano_profile.apps import load_app_state_variable


def completed_at_least_one_challenge(app_name):
    """ Returns True if the user has successfully completed a challenge of the
    specified app.

    ** WARNING **: This only works with the new scheme of tracking progress
    i.e. where there are challenge groups and not a single level

    :param app_name: Name of the app to test progress on
    :type app_name: str

    :returns: True iff user has successfully completed at least one challenge
    :rtype: bool
    """
    prof_var = load_app_state_variable(app_name, 'groups')
    level = 0
    if prof_var:
        try:
            for group in prof_var.itervalues():
                try:
                    level = max(level, group.get('challengeNo', 0))
                except (KeyError, AttributeError, TypeError):
                    continue
        except AttributeError:
            pass
    return level > 0
