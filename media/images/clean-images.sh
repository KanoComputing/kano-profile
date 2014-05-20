#!/usr/bin/env bash

find -path '*originals*' -exec rm -rf {} \; > /dev/null 2>&1

exit 0
