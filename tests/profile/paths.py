import os

PROFILES_PATH = os.path.dirname(__file__)
TEST_PROFILES_PATH = os.path.join(PROFILES_PATH, 'sample_profiles')

def get_profile_files(app):
    app_profile_path = os.path.join(TEST_PROFILES_PATH, app)

    empty_profile_file = os.path.join(app_profile_path, 'empty.json')
    complete_profile_file = os.path.join(app_profile_path, 'complete.json')

    return {
        'empty': empty_profile_file,
        'complete': complete_profile_file
    }

def get_profile_data(app):
    profile_files = get_profile_files(app)
    profile_data = {}

    for key, profile_file in profile_files.iteritems():
        with open(profile_file, 'r') as f:
            data = f.read()

        profile_data[key] = data

    return profile_data
