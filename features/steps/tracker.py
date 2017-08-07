import sys
import os
import json
import subprocess
import signal
from time import sleep
from behave import given, when, then
from behave_pytest.hook import install_pytest_asserts


LOCAL_LIB_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..'
)
sys.path.insert(0, LOCAL_LIB_DIR)

from kano_profile.paths import tracker_dir

def before_all(context):
    install_pytest_asserts()


IDLE_APP = '''
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
'''.format(local_lib_dir=LOCAL_LIB_DIR)
SESSION_ID_TEMPLATE = 'test-proc-{id}'


'''
Given
'''


@given('an app with tracking sessions is launched')
def create_app_step(ctx):
    if not 'procs' in ctx:
        ctx.procs = []

    ctx.procs.append(
        subprocess.Popen([
            'python',
            '-c',
            IDLE_APP.format(
                session_id=SESSION_ID_TEMPLATE.format(id=len(ctx.procs))
            ),
        ])
    )

    try:
        assert ctx.procs[-1].poll() != 0
    except Exception as err:
        print(
            'Process failed to run. Return code: {}'
            .format(ctx.procs[-1].poll())
        )

        raise err


'''
When
'''


@when('{secs:d} seconds elapse')
def wait(ctx, secs):
    sleep(secs)


@when('the app closes')
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
    return os.path.join(tracker_dir, get_session_file(proc, proc_session_id))


@when(u'the tracking session is paused')
def pause_tracking(ctx):
    pause_tracking_sessions()


@when(u'the tracking session is unpaused')
def unpause_tracking(ctx):
    unpause_tracking_sessions()


'''
Then
'''


@then('a tracking session exists')
def tracking_session_exists_step(ctx):
    assert os.path.isdir(tracker_dir)

    for idx, proc in enumerate(ctx.procs):
        session_path = get_session_path(proc, idx)

        try:
            assert os.path.isfile(session_path)
        except Exception as err:
            print("Couldn't find session file: {}".format(session_path))

            raise err


'''
Main check for tracking sessions. Other steps call this.
'''
def tracking_session_check(ctx, proc_idx, secs):
    proc = ctx.procs[proc_idx]
    session_path = get_session_path(proc, proc_idx)

    with open(session_path, 'r') as session_f:
        session_data = json.load(session_f)

    assert session_data['elapsed'] == secs


@then('there is a tracking session log for the app running for {secs:d} seconds')
def tracking_session_check_no_idx_step(ctx, secs):
    tracking_session_check(ctx, 0, secs)


@then('there is a tracking session log for the {proc_no:d}st app running for {secs:d} seconds')
def tracking_session_check_idx_st_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


@then('there is a tracking session log for the {proc_no:d}nd app running for {secs:d} seconds')
def tracking_session_check_idx_nd_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


@then('there is a tracking session log for the {proc_no:d}rd app running for {secs:d} seconds')
def tracking_session_check_idx_rd_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


@then('there is a tracking session log for the {proc_no:d}th app running for {secs:d} seconds')
def tracking_session_check_idx_th_step(ctx, proc_no, secs):
    tracking_session_check(ctx, proc_no - 1, secs)


def after_feature(ctx, feature):
    app_close(ctx)
