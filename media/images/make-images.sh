#!/usr/bin/env bash

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
