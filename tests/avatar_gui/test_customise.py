import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

import json
import pytest


def refresh_gui():
    from gi.repository import Gtk

    while Gtk.events_pending():
        Gtk.main_iteration_do(blocking=False)


class TestCustomise(object):
    DEFAULT_MENU = 'judoka-suits'

    @classmethod
    def setup_class(cls):
        try:
            from kano_avatar.paths import AVATAR_CONF_FILE
        except ImportError as err:
            pytest.skip(
                'Skipping: Failed to import kano_avatar.paths: {}'.format(err)
            )

        with open(AVATAR_CONF_FILE, 'r') as conf_f:
            cls._conf = json.load(conf_f)

        cls._categories = cls._conf.get('categories', [])
        cls._objects = cls._conf.get('objects', [])


    def setup_method(self, method):
        from kano_avatar_gui.customise import show_wardrobe

        self._win = show_wardrobe()
        refresh_gui()


    def teardown_method(self, method):
        self._win.destroy()


    def get_category_objects(self, category_id):
        return [
            obj for obj in self._objects
            if obj.get('category') == category_id
        ]


    def test_default_menu(self):
        char = self._win.char_edit
        char_menu = char._menu

        # Simple check
        assert char_menu.get_selected_category() == TestCustomise.DEFAULT_MENU

        # Popup menu check
        for cat, menu in char_menu.menus.iteritems():
            popup = menu['pop_up']
            if cat != TestCustomise.DEFAULT_MENU:
                assert not popup.get_visible()
                continue

            assert popup.get_visible()

            displayed_items = popup._items.keys()
            displayed_items.sort()

            cat_objs = self.get_category_objects(TestCustomise.DEFAULT_MENU)
            obj_ids = [obj.get('item_id') for obj in cat_objs]
            obj_ids.sort()

            assert displayed_items == obj_ids
