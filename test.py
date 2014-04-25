#!/usr/bin/env python

import sys
import os
from pprint import pprint

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

# from kano.profile.badges import test_badge_rules, calculate_badges, load_badge_rules, create_images
from kano.utils import run_cmd
from kano.world.functions import login_using_token
from kano.world.share import list_shares, upload_share, delete_share

success, value = login_using_token()
if not success:
    run_cmd(dir_path + '/bin/kano-login')
    success, value = login_using_token()
    if not success:
        sys.exit('Login not possible, error: ' + value)



# # kw.glob_session.backup_content()
# # print kw.glob_session.restore_content()
# print kw.glob_session.upload_workspace('README.xml', 'title2', 'appname')
# # success, data = kww.list_workspaces('appname', 0)
# # if success:
#     # pprint(data)

# # for k in data:
# #     pprint(k)
# #     print



# test_badge_rules()
# create_images()
# badges = calculate_badges('badges')
# pprint(badges)



# shares = list_shares(app_name='minecraft')[2]
# pprint(shares)

pprint(upload_share('kanocastle.xml', 'Kano Castle', 'make-minecraft', True))

# delete all shares
# shares = list_shares(featured=False)[2]['entries']
# for share in shares:
#     print[share['user']['username']]
#     print delete_share(share['id'])
