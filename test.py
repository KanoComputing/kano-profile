from pprint import pprint

from kano.utils import get_date_now
from kano.profile.profile import load_profile, save_profile
from kano.profile.badges import calculate_xp
from kano.profile.apps import get_app_list, load_app_state


data = dict()

profile = load_profile()
save_profile(profile)
for k, v in profile.iteritems():
    if k in ['username_linux', 'save_date']:
        data[k] = v

data['xp'] = calculate_xp()
data['upload_date'] = get_date_now()

stats = dict()

for app in get_app_list():
    stats[app] = load_app_state(app)

data['stats'] = stats

pprint(data)
