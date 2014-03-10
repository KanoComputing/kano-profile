#!/usr/bin/env python

# web-cli.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import subprocess
import pwd
import datetime
import parser
from optparse import OptionParser
from requests.compat import json

from web_api import ApiClient as api


# TODO change to kano.utils
def run(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


# TODO change to kano.utils
def read_file_contents_as_lines(path):
    if os.path.exists(path):
        with open(path) as infile:
            content = infile.readlines()
            lines = [line.strip() for line in content]
            return lines


# TODO change to kano.utils
def get_user_environ():
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    else:
        return os.environ['LOGNAME']


# TODO change to kano.utils
def get_home_directory(username):
    return pwd.getpwnam(username).pw_dirs


# TODO change to kano.utils
def get_date_now():
    return datetime.datetime.utcnow().isoformat()


# TODO change to kano.utils
def get_device_id():
    cpuinfo_file = '/proc/cpuinfo'
    lines = read_file_contents_as_lines(cpuinfo_file)

    if not lines:
        return

    for l in lines:
        parts = [p.strip() for p in l.split(':')]
        if parts[0] == 'Serial':
            return parts[1].upper()


# TODO change to kano.utils, CAREFUL!
def get_mac_address():
    cmd = '/sbin/ifconfig -a eth0 | grep HWaddr'
    o, _ = run(cmd)
    if len(o.split('HWaddr')) != 2:
        return

    mac_addr = o.split('HWaddr')[1].strip()
    mac_addr_str = mac_addr.translate(None, ':').upper()

    if len(mac_addr_str) == 12:
        return mac_addr_str


def lister(options, client):
    response = client.get('/share/%s' % options.appname)

    if response and response.status_code is 200:
        print json.dumps(response.json()['files'])


def uploader(options, client):
    if not options.filepath:
        parser.error("Please specific a --file option")

    exitCode = 1

    files = {
        'file': open(options.filepath, 'rb')
    }

    data = {
        'device_id': get_device_id(),
        'device_username': get_user_environ(),
        'device_mac_addr': get_mac_address()
    }

    if os.getenv('KANO_DATA_OVERRIDES'):
        data.update(json.loads(os.getenv('KANO_DATA_OVERRIDES')))

    response = None
    try:
        response = client.post('/share/%s' % options.appname,
                               files=files, data=data)
    except api.Error:
        # probably should log the error here?
        pass

    if response and response.status_code is 201:
        exitCode = 0

    exit(exitCode)


def main():
    usage = "usage: %prog [--upload|--download]"
    parser = OptionParser(usage=usage)
    parser.add_option('--upload', dest='isUploader', action='store_true')
    parser.add_option('--list', dest='isLister', action='store_true')
    parser.add_option('-f', '--file', dest='filepath', action="store", type='string')
    parser.add_option('-a', '--app', dest='appname', action="store", type='string')

    (options, args) = parser.parse_args()

    if not options.appname:
        parser.error("Please specific a --app option")

    client = api.ApiClient()
    if os.getenv("KANO_API_HOST", False):
        client.API_HOST = os.getenv("KANO_API_HOST")

    if options.isLister:
        return lister(options, client)

    if options.isUploader:
        return uploader(options, client)

if __name__ == "__main__":
    main()
