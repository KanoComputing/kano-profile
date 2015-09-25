#!/usr/bin/env bash
# To run this script, you need:
# pip install kiwimasher
# apt-get install pngquant
# apt-get install advancecomp


kiwimasher -t png8 -s png -o -c$1 -p resize_fill 230 180 --no-suffix --skip
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 460 448 --no-suffix --skip
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 590 270 --no-suffix --skip




