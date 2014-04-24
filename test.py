#!/usr/bin/env python

import sys
import os
from pprint import pprint

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

# import kano.world.functions as kw
# import kano.world.workspaces as kww
# from kano.utils import run_cmd

# # login first with token, if not working then try with dialog
# success, value = kw.login_using_token()
# if not success:
#     run_cmd(dir_path + '/bin/kano-login')
#     success, value = kw.login_using_token()
#     if not success:
#         sys.exit('Login not possible, error: ' + value)

# # kw.glob_session.backup_content()
# # print kw.glob_session.restore_content()
# print kw.glob_session.upload_workspace('README.xml', 'title2', 'appname')
# # success, data = kww.list_workspaces('appname', 0)
# # if success:
#     # pprint(data)

# # for k in data:
# #     pprint(k)
# #     print


from kano.profile.badges import test_badge_rules, calculate_badges, load_badge_rules

test_badge_rules()
# badges = calculate_badges()
# pprint(badges)
