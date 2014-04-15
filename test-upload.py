#!/usr/bin/env python

import sys

import kano.world as kw


success, value = kw.login_using_token()
if not success:
    sys.exit('Login not possible, error: ' + value)

# kw.glob_session.backup_content()
print kw.glob_session.restore_content()

