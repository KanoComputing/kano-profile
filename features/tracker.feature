Feature: App tracker

    Scenario: An app runs and creates a tracking session
        Given an app with tracking sessions is launched
         When 2 seconds elapse
          And the app closes
         Then a tracking session exists
          And there is a tracking session log for the app running for 2 seconds


    Scenario: A tracked app is running and the session is paused
        Given an app with tracking sessions is launched
         When 1 seconds elapse
          And the tracking session is paused
          And 2 seconds elapse
          And the tracking session is unpaused
          And 2 seconds elapse
         When the app closes
         Then 2 tracking sessions exist
          And there is a tracking session log for the 1st app running for 1 seconds
          And there is a tracking session log for the 1st app running for 2 seconds


    Scenario: The tracked app closes while the tracking is paused
        Given the tracking session is paused
         When 1 seconds elapse
          And an app with tracking sessions is launched
          And 2 seconds elapse
          And the app closes
          And 2 seconds elapse
          And the tracking session is unpaused
         Then no tracking sessions exist


    Scenario: A tracked app opens and closes while the tracking is paused
        Given an app with tracking sessions is launched
         When 1 seconds elapse
          And the tracking session is paused
          And 2 seconds elapse
          And the app closes
          And 2 seconds elapse
          And the tracking session is unpaused
         Then a tracking session exists
          And there is a tracking session log for the app running for 1 seconds


    Scenario: The tracked app opens after the tracking is paused
        Given the tracking session is paused
         When 1 seconds elapse
          And an app with tracking sessions is launched
          And 2 seconds elapse
          And the tracking session is unpaused
          And 2 seconds elapse
          And the app closes
         Then a tracking session exists
          And there is a tracking session log for the app running for 2 seconds


    Scenario: Tracking pausing is requested multiple times
        Given an app with tracking sessions is launched
         When 1 seconds elapse
          And the tracking session is paused
          And 1 seconds elapse
          And the tracking session is paused
          And 1 seconds elapse
          And the tracking session is unpaused
          And 2 seconds elapse
          And the app closes
         Then 2 tracking sessions exist
          And there is a tracking session log for the 1st app running for 1 seconds
          And there is a tracking session log for the 1st app running for 2 seconds
