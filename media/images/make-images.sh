#!/usr/bin/env bash

# make-images.sh
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Generates the locked versions of the assets along with the resized assets

./generate-locked-versions.py

level=2

cd badges
./generate-images.sh $level
cd ..

cd environments
./generate-images.sh $level
cd ..

cd progress_icons
./generate-images.sh $level
cd ..

gfind -path '*.tmp*' -exec rm {} \;
