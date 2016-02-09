import os

LOCAL_RULES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'rules')
)
INSTALLED_RULES_PATH = os.path.join(
    os.path.sep, 'usr', 'share', 'kano-profile', 'rules'
)


RULES_FILES = [
    'app_profiles.json',
    'levels.json',
    'xp.json',
    'badges/application.json',
    'badges/easter_eggs.json',
    'badges/in_game.json',
    'badges/master.json',
    'badges/number.json',
    'badges/online.json',
    'environments/all.json',
    'avatar_generator/conf.json'
]
RULES_SETUP = []

for rule_file in RULES_FILES:
    with open(os.path.join(LOCAL_RULES_PATH, rule_file), 'r') as f:
        rule = f.read()

    RULES_SETUP.append(
        (
            os.path.join(INSTALLED_RULES_PATH, rule_file),
            os.path.join(LOCAL_RULES_PATH, rule_file),
            rule
        )
    )
