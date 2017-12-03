#
# tracker.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Steps for tracking features
#


import sys
import os
import json
import subprocess
import signal
from time import sleep
from textwrap import dedent
from behave import given, when, then


LOCAL_LIB_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..'
)
sys.path.insert(0, LOCAL_LIB_DIR)
SESSION_ID_TEMPLATE = 'test-proc-{id}'


def list_tracking_files():
    from kano_profile.paths import tracker_dir, PAUSED_SESSIONS_FILE

    return [
        os.path.join(tracker_dir, f) for f in os.listdir(tracker_dir)
        if os.path.join(tracker_dir, f) != PAUSED_SESSIONS_FILE
    ]

def create_app(ctx):
    if not 'procs' in ctx:
        ctx.procs = []


    # A simple tracked app which does nothing but stay alive.
    idle_app = dedent('''
        import sys
        import atexit
        from time import sleep

        sys.path.insert(0, "{local_lib_dir}")
        from kano_profile.tracker import session_start, session_end

        SESSION_FILE = session_start('{{session_id}}')

        def cleanup():
            session_end(SESSION_FILE)
        atexit.register(cleanup)

        while True:
            sleep(1)
    ''').format(local_lib_dir=LOCAL_LIB_DIR)

    session_id = SESSION_ID_TEMPLATE.format(id=len(ctx.procs))
    proc = subprocess.Popen([
        'python',
        '-c',
        idle_app.format(
            session_id=session_id
        ),
    ])
    proc.session_id = session_id
    ctx.procs.append(proc)

    try:
        assert ctx.procs[-1].poll() != 0
    except Exception as err:
        print(
            'Process failed to run. Return code: {}'
            .format(ctx.procs[-1].poll())
        )

        raise err


'''
Given
'''


@given(u'an app with tracking sessions is launched')
def given_app_created_step(ctx):
    create_app(ctx)


@given(u'the tracking session is paused')
def tracking_paused_step(ctx):
    from kano_profile.tracker import pause_tracking_sessions

    pause_tracking_sessions()


'''
When
'''


@when(u'{secs:d} seconds elapse')
def wait(ctx, secs):
    sleep(secs)


@when(u'the app closes')
def app_close(ctx):
    for proc in ctx.procs:
        proc.send_signal(signal.SIGINT)
        proc.wait()


def get_session_file(proc, proc_session_id):
    return '{pid}-{name}.json'.format(
        pid=proc.pid,
        name=SESSION_ID_TEMPLATE.format(id=proc_session_id)
    )


def get_session_path(proc, proc_session_id):
    from kano_profile.paths import tracker_dir

    return os.path.join(tracker_dir, get_session_file(proc, proc_session_id))


@when(u'the tracking session is paused')
def pause_tracking(ctx):
    from kano_profile.tracker import pause_tracking_sessions

    pause_tracking_sessions()


@when(u'the tracking session is unpaused')
def unpause_tracking(ctx):
    from kano_profile.tracker import unpause_tracking_sessions

    unpause_tracking_sessions()


@when(u'an app with tracking sessions is launched')
def launch_app_step(ctx):
    create_app(ctx)


'''
Then
'''


@then(u'{num:d} tracking sessions exist')
def n_tracking_session_exists_step(ctx, num):
    from kano_profile.paths import tracker_dir

    assert os.path.isdir(tracker_dir)

    tracking_sessions = list_tracking_files()
    assert len(tracking_sessions) == num


@then(u'a tracking session exists')
def tracking_session_exists_step(ctx):
    n_tracking_session_exists_step(ctx, 1)


@then(u'no tracking sessions exist')
def no_tracking_session_exists_step(ctx):
    n_tracking_session_exists_step(ctx, 0)


'''
Main check for tracking sessions. Other steps call this.
'''
def tracking_session_check(ctx, proc_idx, secs):
    from kano_profile.tracker.tracking_session import TrackingSession

    proc = ctx.procs[proc_idx]
    session = TrackingSession(name=proc.session_id, pid=proc.pid)

    for session_path in list_tracking_files():
        with open(session_path, 'r') as session_f:
            session_data = json.load(session_f)

        if session_data['name'] == session.name and \
                session_data['pid'] == session.pid:
            if session_data['elapsed'] == secs:
                assert True
                return

    assert False


@then(u'there is a tracking session log for the app running for {secs:d} seconds')
def tracking_session_check_no_idx_step(ctx, secs):
    tracking_session_check(ctx, 0, secs)


@then(u'there is a tracking session log for the {proc_no:d}st app running for {secs:d} seconds')
def tracking_session_check_idx_st_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


@then(u'there is a tracking session log for the {proc_no:d}nd app running for {secs:d} seconds')
def tracking_session_check_idx_nd_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


@then(u'there is a tracking session log for the {proc_no:d}rd app running for {secs:d} seconds')
def tracking_session_check_idx_rd_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


@then(u'there is a tracking session log for the {proc_no:d}th app running for {secs:d} seconds')
def tracking_session_check_idx_th_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


def after_feature(ctx, feature):
    app_close(ctx)
