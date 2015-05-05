#!/usr/bin/env python

# generate-locked-versions.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This script generates the locked vesions of the assets
import os

dirpath = os.getcwd()

for root, dirs, filenames in os.walk(dirpath):
    for filename in filenames:
        path_full = os.path.join(root, filename)
        path_rel = os.path.relpath(path_full, dirpath)
        dir_path_full = os.path.dirname(path_full)
        dir_path_rel = os.path.relpath(dir_path_full, dirpath)
        if dir_path_rel == '.':
            dir_path_rel = ''
        basename, ext = os.path.splitext(filename)
        ext = ext[1:]

        if ext != 'png':
            continue

        dir_path_split = dir_path_rel.split('/')

        if dir_path_split[0] not in ['environments', 'badges']:
            continue
        if len(dir_path_split) < 2 or dir_path_split[1] != 'originals':
            continue
        if basename.endswith('_locked') or basename.endswith('_circular') or basename.endswith('_levelup'):
            continue

        new_filename_rel = os.path.join(dir_path_rel, basename + '_locked.png')
        new_filename_abs = os.path.join(dirpath, new_filename_rel)

        src_date = os.path.getmtime(path_full)
        if os.path.exists(new_filename_abs):
            target_date = os.path.getmtime(new_filename_abs)
            if src_date == target_date:
                continue

        convert_cmd = 'convert {} -matte -channel A +level 0,30% +channel {}'.format(path_full, new_filename_abs)
        print path_rel
        os.system(convert_cmd)
        os.utime(new_filename_abs, (src_date, src_date))



