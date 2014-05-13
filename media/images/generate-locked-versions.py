#!/usr/bin/env python

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

        dir_path_split = dir_path_rel.split('/')

        if dir_path_split[0] not in ['environments', 'avatars', 'badges']:
            continue
        if len(dir_path_split) < 2 or dir_path_split[1] != 'originals':
            continue
        if basename.endswith('_locked') or basename.endswith('_circular'):
            continue

        new_filename_rel = os.path.join(dir_path_rel, basename + '_locked.png')
        new_filename_abs = os.path.join(dirpath, new_filename_rel)

        convert_cmd = 'convert {} -matte -channel A +level 0,30% +channel {}'.format(path_full, new_filename_abs)
        print path_rel
        os.system(convert_cmd)

