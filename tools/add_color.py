#!/usr/bin/env python

# add_color.py
# 
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# 

import os
import sys
if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from kano.utils import read_json, write_json

basedir = '../rules/badges'
files = os.listdir(basedir)
for f in files:
    f = os.path.join(basedir, f)
    data = read_json(f)
    if not data:
        continue
    for item in data.iterkeys():
        data[item]['bg_color'] = '000000'
    write_json(f, data, prettyprint=True)

