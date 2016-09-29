#!/usr/bin/env python
# # -*- coding: utf-8 -*- 

# test_email_validation.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Tests that the new email validation returns errors for unsupported characters
#

import unittest

import sys
sys.path.insert(1, '..')

from kano_registration_gui.RegistrationScreen import validate_email

class TestEmailValidation(unittest.TestCase):

    def test_email_ok(self):
        msg = validate_email('someone@somewhere.good')
        self.assertIsNone(msg)
    
    def test_email_empty(self):
        msg = validate_email('')
        self.assertIsNotNone(msg)

    def test_email_no_dot_no_atsign(self):
        msg = validate_email('notgood')
        self.assertIsNotNone(msg)

    def test_email_dots_no_atsign(self):
        msg = validate_email('almost.good.but.not')
        self.assertIsNotNone(msg)

    def test_email_with_tilde(self):
        msg = validate_email('iñaki@mydomain.yeah')
        self.assertIsNotNone(msg)

    def test_email_with_capital_tilde(self):
        msg = validate_email('IÑAKI@mydomain.yeah')
        self.assertIsNotNone(msg)

    def test_email_with_accent(self):
        msg = validate_email('mercè@mydomain.yeah')
        self.assertIsNotNone(msg)

    def test_email_with_spaces(self):
        msg = validate_email('who on earth are you@nobody.knows')
        self.assertIsNotNone(msg)

    def test_email_with_colons(self):
        msg = validate_email('i;am,a,bit;silly@home.eu')
        self.assertIsNotNone(msg)

    def test_email_with_many_domains(self):
        msg = validate_email('paul@i.live.really.very.far.away')
        self.assertIsNone(msg)


if __name__ == '__main__':
    unittest.main()
