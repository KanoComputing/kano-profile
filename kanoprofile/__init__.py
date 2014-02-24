import sys
import getpass
import datetime
import os
import grp
import json
import subprocess
import pwd

__version__ = '0.1'


# helper functions


def ensuredir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def read_file_contents(path):
    if os.path.exists(path):
        with open(path) as infile:
            return infile.read().strip()


def read_file_contents_as_lines(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return lines


def run(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


def run_term_on_error(cmd):
    o, e = run(cmd)
    if e:
        print e
        quit(1)


def get_user_getpass():
    return getpass.getuser()


def get_user_logname():
    o, _ = run('logname')
    return o.strip()


def get_user_environ():
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    else:
        return os.environ['LOGNAME']


def get_home_directory(username):
    return pwd.getpwnam(username).pw_dir


def get_date_now():
    return datetime.datetime.utcnow().isoformat()


def get_device_id():
    cpuinfo_file = '/proc/cpuinfo'
    lines = read_file_contents_as_lines(cpuinfo_file)

    for l in lines:
        parts = [p.strip() for p in l.split(':')]
        if parts[0] == 'Serial':
            return parts[1].upper()


def get_mac_address():
    cmd = '/sbin/ifconfig -a eth0 | grep HWaddr'
    o, _ = run(cmd)
    if len(o.split('HWaddr')) != 2:
        return
    mac_addr = o.split('HWaddr')[1].strip()
    mac_addr_str = mac_addr.translate(None, ':').upper()
    if len(mac_addr_str) == 12:
        return mac_addr_str


# kanoprofile functions


def load_profile():
    if not os.path.exists(profile_file):
        data = dict()
    else:
        try:
            data = json.loads(read_file_contents(profile_file))
        except Exception:
            data = dict()

    if 'username_linux' not in data:
        data['username_linux'] = linux_user

    if 'email' not in data and get_email_from_disk():
        data['email'] = get_email_from_disk()

    if 'device_id' not in data and get_device_id():
        data['device_id'] = get_device_id()

    if 'mac_addr' not in data and get_mac_address():
        data['mac_addr'] = get_mac_address()

    return data


def save_profile(data):
    data['last_save_date'] = get_date_now()
    data['last_save_version'] = __version__
    with open(profile_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def get_email_from_disk():
    kano_email_file = os.path.join(home_directory, '.useremail')
    return read_file_contents(kano_email_file)


def get_app_dir(app_name):
    app_dir = os.path.join(apps_dir, app_name)
    ensuredir(app_dir)
    return app_dir


def get_app_data_dir(app_name):
    data_str = 'data'
    app_data_dir = os.path.join(get_app_dir(app_name), data_str)
    ensuredir(app_data_dir)
    return app_data_dir


def get_app_state_file(app_name):
    app_state_str = 'state.json'
    app_state_file = os.path.join(get_app_dir(app_name), app_state_str)
    return app_state_file


def load_app_state(app_name):
    app_state_file = get_app_state_file(app_name)

    if not os.path.exists(app_state_file):
        data = dict()
    else:
        try:
            data = json.loads(read_file_contents(app_state_file))
        except Exception:
            data = dict()

    return data


def save_app_state(app_name, data):
    app_state_file = get_app_state_file(app_name)

    data['last_save_date'] = get_date_now()
    with open(app_state_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


def calculate_xp():
    try:
        allrules = json.loads(read_file_contents(rules_file))
    except Exception:
        return 0

    points = 0

    for app, groups in allrules.iteritems():
        appstate = load_app_state(app)
        for group, rules in groups.iteritems():

            # calculating points based on level
            if group == 'level':
                maxlevel = int(appstate['level'])

                for level, value in rules.iteritems():
                    level = int(level)
                    value = int(value)

                    if level <= maxlevel:
                        points += value

            # calculating points based on multipliers
            if group == 'multipliers':
                for thing, value in rules.iteritems():
                    value = float(value)
                    if thing in appstate:
                        points += value * appstate[thing]

    return points


def get_gamestate_variables(app_name):
    try:
        allrules = json.loads(read_file_contents(rules_file))
    except Exception:
        return list()

    groups = allrules[app_name]

    for group, rules in groups.iteritems():
        if group == 'multipliers':
            return [str(key) for key in rules.keys()]


# start
if __name__ == "__main__":
    sys.exit("Should be imported as module")

# checking kanousers group
try:
    kanogrp = grp.getgrnam('kanousers')
    kanomembers = kanogrp.gr_mem
except KeyError:
    sys.exit("kanousers group doesn't exist")

# getting linux variables
linux_user = get_user_environ()
home_directory = get_home_directory(linux_user)
module_file = os.path.realpath(__file__)
module_dir = os.path.dirname(module_file)

# check if run under kanouser (or sudo-ed kanouser)
if linux_user not in kanomembers:
    sys.exit("You are not member of kanousers group")

# constructing paths of directories, files
kanoprofile_dir_str = '.kanoprofile'
kanoprofile_dir = os.path.join(home_directory, kanoprofile_dir_str)

profile_dir_str = 'profile'
profile_dir = os.path.join(kanoprofile_dir, profile_dir_str)

apps_dir_str = 'apps'
apps_dir = os.path.join(kanoprofile_dir, apps_dir_str)

profile_file_str = 'profile.json'
profile_file = os.path.join(profile_dir, profile_file_str)

rules_file_str = 'rules.json'
rules_file = os.path.join(module_dir, rules_file_str)

# initializing profile
profile = load_profile()

if not os.path.exists(profile_file):
    ensuredir(profile_dir)
    save_profile(profile)


