#
# Makefile
#
# Copyright (C) 2017 - 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#

REPO:= kano-profile

#
# Add test targets
#
include pythontest.mk
check: pythontest
test: check
