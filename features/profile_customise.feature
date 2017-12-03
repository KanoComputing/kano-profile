#
# profile_customise.feature
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Profile customisation window feature specification
#


@gtk
Feature: Kano Profile Customise
    Scenario: Starts up in the correct configuration
        Given the kano-profile-customise app is loaded
         When the app shows
         Then the "Suits" menu is shown
