#!/usr/bin/env python

# upload-share.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#

import sys
import os
from pprint import pprint

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano.utils import run_cmd
from kano_world.functions import login_using_token
from kano_world.share import upload_share

success, value = login_using_token()
if not success:
    run_cmd(dir_path + '/bin/kano-login')
    success, value = login_using_token()
    if not success:
        sys.exit("Login not possible, error: " + value)

pprint(upload_share('kanocastle.xml', 'Kano Castle', 'make-minecraft'))
