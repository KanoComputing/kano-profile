import os
import re
import json

from kano.logging import logger
from kano_profile.paths import tracker_dir
from kano_profile.tracker.tracking_utils import is_pid_running, open_locked


class TrackingSession(object):
    SESSION_FILE_RE = re.compile(r'^(\d+)-(.*).json$')

    def __init__(self, session_file=None, name=None, pid=None):
        if session_file:
            self._file = os.path.basename(session_file)
            self._pid, self._name = self.parse_session_file(self.file)
        elif name and pid:
            self._name = name
            self._pid = int(pid)
            self._file = self.parse_name_and_pid(self.name, self.pid)

        else:
            raise TypeError(
                'TrackingSession requires a file or a name/pid combination'
            )

    def parse_session_file(self, session_file):
        matches = TrackingSession.SESSION_FILE_RE.findall(session_file)

        if not matches:
            return None, None

        match_data = matches[0]

        pid = int(match_data[0])
        name = match_data[1]

        return pid, name

    def parse_name_and_pid(self, name, pid):
        return "{}-{}.json".format(pid, name)

    def __repr__(self):
        return 'Tracking Session [Name: {name}, PID: {pid}]: {is_open}'.format(
            name=self.name,
            pid=self.pid,
            is_open='OPEN' if self.is_open() else 'CLOSED'
        )

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.file == other.file

    @property
    def file(self):
        return self._file

    @property
    def path(self):
        return os.path.join(tracker_dir, self.file)

    @property
    def name(self):
        return self._name.encode('utf-8')

    @property
    def pid(self):
        return self._pid or 0

    def is_open(self):
        return is_pid_running(self.pid)

    def open(self, mode):
        try:
            session_f = open_locked(self.path, mode)
        except IOError as exc:
            logger.error(
                'Error opening the tracking session file "{f}": {err}'
                .format(f=self.path, err=exc)
            )
        else:
            yield session_f

    def dumps(self):
        return json.dumps({
            'name': self.name,
            'pid': self.pid
        })

    @staticmethod
    def loads(session):
        session_data = json.loads(session.rstrip().lstrip())
        return TrackingSession(
            name=session_data.get('name'),
            pid=session_data.get('pid')
        )
