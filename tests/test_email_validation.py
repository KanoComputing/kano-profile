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
import pytest
sys.path.insert(1, '..')


# Used to display validated emails on the console
print_emails = True


@pytest.mark.gtk
class TestEmailValidation(unittest.TestCase):

    def _validate(self, address):
        from kano_registration_gui.RegistrationScreen import validate_email

        return validate_email(address, verbose=print_emails)

    def test_email_ok(self):
        msg = self._validate('someone@somewhere.good')
        self.assertIsNone(msg)

    def test_email_empty(self):
        msg = self._validate('')
        self.assertIsNotNone(msg)

    def test_email_no_dot_no_atsign(self):
        msg = self._validate('notgood')
        self.assertIsNotNone(msg)

    def test_email_dots_no_atsign(self):
        msg = self._validate('almost.good.but.not')
        self.assertIsNotNone(msg)

    def test_email_many_atsigns(self):
        msg = self._validate('too@many@at@signs.com')
        self.assertIsNotNone(msg)

    def test_email_special_chars(self):
        msg = self._validate('a"b(c)d,e:f;g<h>i[j\k]l@example.com')
        self.assertIsNotNone(msg)

    def test_email_quoted(self):
        msg = self._validate('just"not"right@example.com')
        self.assertIsNotNone(msg)

    def test_email_escaped_quotes(self):
        msg = self._validate('this\ still\"not\\allowed@example.com')
        self.assertIsNotNone(msg)

    def test_email_username_two_consecutive_dots(self):
        msg = self._validate('john..doe@example.com')
        self.assertIsNotNone(msg)

    def test_email_username_with_dots(self):
        msg = self._validate('i.am.someone@example.com')
        self.assertIsNone(msg)

    def test_email_with_tilde(self):
        msg = self._validate('iñaki@mydomain.yeah')
        self.assertIsNotNone(msg)

    def test_email_with_capital_tilde(self):
        msg = self._validate('IÑAKI@mydomain.yeah')
        self.assertIsNotNone(msg)

    def test_email_with_accent(self):
        msg = self._validate('mercè@mydomain.yeah')
        self.assertIsNotNone(msg)

    def test_email_with_spaces(self):
        msg = self._validate('who on earth are you@nobody.knows')
        self.assertIsNotNone(msg)

    def test_email_with_colons(self):
        msg = self._validate('i;am,a,bit;silly@home.eu')
        self.assertIsNotNone(msg)

    def test_email_with_many_domains(self):
        msg = self._validate('paul@i.live.really.very.far.away')
        self.assertIsNone(msg)


if __name__ == '__main__':
    unittest.main()
