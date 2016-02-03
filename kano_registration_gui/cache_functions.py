# cache_functions.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#


from kano_profile.apps import load_app_state_variable, save_app_state_variable


def cache_data(category, value):
    if category in ["username", "email"]:
        save_app_state_variable("kano-avatar-registration", category, value)


def get_cached_data(category):
    return load_app_state_variable("kano-avatar-registration", category)


def cache_emails(email):
    cache_data("email", email)


def cache_all(email, secondary_email, username,
              birthday_day, birthday_month, birthday_year,
              marketing_enabled):
    cache_data("email", email)
    cache_data("username", username)
