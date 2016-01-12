# tracking_helpers.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Helper functions and classes used for tracking

from datetime import datetime
from uuid import uuid4

from kano_profile import tracker


class ChallengeProgressTracker(object):
    CHALLENGE = 'challenge'
    PLAYGROUND = 'playground'

    UNLOCKED = 'unlocked'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'

    def __init__(self):
        self._tracking_mode = None
        self._chal_group = None
        self._chal_no = None
        self._chal_outcome = None
        self._app_session_id = str(uuid4())

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
        self.clear_current_tracking()

        self._tracking_mode = ChallengeProgressTracker.CHALLENGE
        self._chal_group = challenge_group
        self._chal_no = challenge_no
        self._chal_outcome = ChallengeProgressTracker.ABANDONED
        self._start_timestamp = datetime.now()

    def unlocked_challege(self, challenge_group, challenge_no):
        if self._tracking_mode == ChallengeProgressTracker.CHALLENGE and \
                self._chal_group == challenge_group and \
                self._chal_no == challenge_no:
            self._chal_outcome = ChallengeProgressTracker.UNLOCKED

    def completed_challenge(self, challenge_group, challenge_no):
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
                        'app_session': self._app_session_id,
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
                        'app_session': self._app_session_id,
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


challenge_progress_tracker = ChallengeProgressTracker()
