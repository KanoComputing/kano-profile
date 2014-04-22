#!/usr/bin/env python

import sys

import kano.world as kw
import kano.world.workspaces as kww
from pprint import pprint


success, value = kw.login_using_token()
if not success:
    sys.exit('Login not possible, error: ' + value)

# kw.glob_session.backup_content()
# print kw.glob_session.restore_content()
# print kw.glob_session.upload_workspace('README.xml', 'title', 'appname')
success, data = kww.list_workspaces('appname')

for k in data:
    pprint(k)
    print


