#!/usr/bin/env python

# test.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Runs all the unit tests
#


import sys
import os
import unittest

sys.path.insert(
    1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)


SUITE = unittest.TestSuite()
TESTS = [
    'tests.profile.test_pong',
    'tests.profile.test_mc'
]

for test in TESTS:
    SUITE.addTest(unittest.defaultTestLoader.loadTestsFromName(test))

unittest.TextTestRunner(verbosity=2).run(SUITE)
