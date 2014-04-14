#!/usr/bin/env python

import requests
import sys

from kano.world import api_url


if len(sys.argv) != 2:
    sys.exit('Wrong usage, needs to supply code')
else:
    code = sys.argv[1]

r = requests.post(api_url + '/accounts/activate/' + code)

print r.text
