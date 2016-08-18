#!/usr/bin/env python

# activate_account.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#

import sys
import os
import requests

# TODO: Remove this statement after upgrading to a friendly Python-requests match
requests.packages.urllib3.disable_warnings()

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)


from kano_world.connection import api_url

if len(sys.argv) != 2:
    sys.exit("Wrong usage, needs to supply code")
else:
    code = sys.argv[1]

# Provide 2 separate timeouts - for CONNECT and READ, to requests library
connect_timeout = 5
read_timeout = 20

r = requests.post(api_url + '/accounts/activate/' + code,
                  timeout=(connect_timeout, read_timeout))

print r.text
