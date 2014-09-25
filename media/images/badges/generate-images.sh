#!/usr/bin/env bash

kiwimasher -t png8 -s png -o -c$1 -p resize_fill 230 180 --no-suffix --skip
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 460 448 --no-suffix --skip
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 590 270 --no-suffix --skip




