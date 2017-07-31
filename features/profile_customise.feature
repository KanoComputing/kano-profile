Feature: Kano Profile Customise
    Scenario: Starts up in the correct configuration
        Given the kano-profile-customise app is loaded
         When the app shows
         Then the "Suits" menu is shown
