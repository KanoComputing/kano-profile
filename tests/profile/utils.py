def parse_badges(badges):
    parsed_badges = []
    for badge_types in badges.itervalues():
        parsed_badges += [
            badge_name for badge_name, badge_data in badge_types.iteritems()
            if badge_data['achieved']
        ]

    return parsed_badges

def parse_environments(envs):
    return [env for env in envs.iterkeys()]
