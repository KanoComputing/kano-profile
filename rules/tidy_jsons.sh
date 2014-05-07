#!/usr/bin/env bash

find . -name '*.json' -exec underscore print -i {} -o {} \;
