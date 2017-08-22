import atexit

from kano.utils.processes import get_program_name
from kano_profile.tracker.tracking_sessions import session_start, session_end


class Tracker(object):
    """Tracker class, used for measuring program run-times,
    implemented via atexit hooks"""

    def __init__(self):
        self.path = session_start(get_program_name())
        atexit.register(self._write_times)

    def _write_times(self):
        session_end(self.path)
