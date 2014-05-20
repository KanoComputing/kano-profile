#!/usr/bin/env bash

kiwimasher -t png8 -s png -o -c$1 -p resize_fill 54 54 --no-suffix
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 230 180 --no-suffix
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 460 448 --no-suffix
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 590 270 --no-suffix
kiwimasher -t png8 -s png -o -c$1 -p resize_fill 734 404 --no-suffix



