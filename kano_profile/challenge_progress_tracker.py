# tracking_helpers.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Helper functions and classes used for tracking

from os import getpid
from datetime import datetime

from kano.utils.processes import get_program_name
from kano.logging import logger


from . import tracker
from .tracker import get_session_unique_id


class ChallengeProgressTracker(object):
    CHALLENGE = 'challenge'
    PLAYGROUND = 'playground'

    UNLOCKED = 'unlocked'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'

    _singleton_instance = None

    @staticmethod
    def get_instance():
        if not ChallengeProgressTracker._singleton_instance:
            ChallengeProgressTracker()

        return ChallengeProgressTracker._singleton_instance

    def __init__(self):
        if ChallengeProgressTracker._singleton_instance:
            raise Exception("This class is a singleton!")
        else:
            ChallengeProgressTracker._singleton_instance = self

        app_name = get_program_name()
        session_uuid = get_session_unique_id(app_name, getpid())

        if not session_uuid:
            logger.warn(
                "Session id doesn't exist, is there an app session running?"
            )

        self._app_name = app_name
        self._tracking_mode = None
        self._chal_group = None
        self._chal_no = None
        self._chal_outcome = None
        self._app_session_id = session_uuid

    def set_name(self, app_name):
        if not isinstance(app_name, basestring):
            raise TypeError("set_name argument must be of type string")

        if app_name:
            self._app_name = app_name
        else:
            raise ValueError("App name must not be empty")

    def _check_name_is_set(self):
        if not self._app_name:
            raise RuntimeError(
                "App name is not set for this instance of {}. " \
                "Please run the set_name method"
                .format(self.__class__.__name__)
            )

    def clear_current_tracking(self):
        if self._tracking_mode == ChallengeProgressTracker.CHALLENGE:
            # TODO: LOG THEM HERE
            self._clean_up_challenge_tracking()
        elif self._tracking_mode == ChallengeProgressTracker.PLAYGROUND:
            self._clean_up_playground_tracking()

    def _clean_up_challenge_tracking(self):
        self._chal_group = None
        self._chal_no = None
        self._start_timestamp = None
        self._chal_outcome = None

    def start_challenge(self, challenge_group, challenge_no):
        self._check_name_is_set()
        self.clear_current_tracking()

        self._tracking_mode = ChallengeProgressTracker.CHALLENGE
        self._chal_group = challenge_group
        self._chal_no = challenge_no
        self._chal_outcome = ChallengeProgressTracker.ABANDONED
        self._start_timestamp = datetime.now()

    def unlocked_challege(self, challenge_group, challenge_no):
        self._check_name_is_set()
        if self._tracking_mode == ChallengeProgressTracker.CHALLENGE and \
                self._chal_group == challenge_group and \
                self._chal_no == challenge_no:
            self._chal_outcome = ChallengeProgressTracker.UNLOCKED

    def completed_challenge(self, challenge_group, challenge_no):
        self._check_name_is_set()
        if self._tracking_mode == ChallengeProgressTracker.CHALLENGE and \
                self._chal_group == challenge_group and \
                self._chal_no == challenge_no and \
                self._chal_outcome != ChallengeProgressTracker.UNLOCKED:
            self._chal_outcome = ChallengeProgressTracker.COMPLETED

    def stop_challenge(self, challenge_group, challenge_no):
        # TODO Add check for other modes
        if self._tracking_mode == ChallengeProgressTracker.CHALLENGE and \
                self._chal_group == challenge_group and \
                self._chal_no == challenge_no:
            try:
                attempt_length = datetime.now() - self._start_timestamp
                tracker.track_data(
                    'challenge-attempt',
                    {
                        'app_name': self._app_name,
                        'app_session_id': self._app_session_id,
                        'challenge_group': self._chal_group,
                        'challenge_no': self._chal_no,
                        'outcome': self._chal_outcome,
                        'length_sec': attempt_length.total_seconds()
                    }
                )
            except:
                pass

            self._clean_up_challenge_tracking()

    def _clean_up_playground_tracking(self):
        self._current_hw_ref = None
        self._start_timestamp = None

    def start_playground(self, hw_ref):
        self._check_name_is_set()
        self.clear_current_tracking()

        self._tracking_mode = ChallengeProgressTracker.PLAYGROUND
        self._current_hw_ref = hw_ref
        self._start_timestamp = datetime.now()

    def stop_playground(self, hw_ref):
        if self._tracking_mode == ChallengeProgressTracker.PLAYGROUND and \
                self._current_hw_ref == hw_ref:
            try:
                attempt_length = datetime.now() - self._start_timestamp
                tracker.track_data(
                    'playground-session',
                    {
                        'app_name': self._app_name,
                        'app_session_id': self._app_session_id,
                        'hw_ref': self._current_hw_ref,
                        'length_sec': attempt_length.total_seconds()
                    }
                )
            except:
                pass
            self._clean_up_playground_tracking()

    def stop_all(self):
        if self._tracking_mode == ChallengeProgressTracker.CHALLENGE:
            self.stop_challenge(self._chal_group, self._chal_no)
        elif self._tracking_mode == ChallengeProgressTracker.PLAYGROUND:
            self.stop_playground(self._current_hw_ref)
