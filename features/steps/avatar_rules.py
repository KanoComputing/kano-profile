import json


def load_config():
    from kano_avatar.paths import AVATAR_CONF_FILE

    with open(AVATAR_CONF_FILE, 'r') as conf_f:
        return json.load(conf_f)


def get_category_objects(category_id):
    conf = load_config()
    objects = conf.get('objects', [])

    return [
        obj for obj in objects
        if obj.get('category') == category_id
    ]


def get_category_id_from_label(category_label):
    conf = load_config()
    categories = conf.get('categories', [])

    for cat in categories:
        if cat.get('display_name') == category_label:
            return cat.get('category_id')
