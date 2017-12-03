import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

import pytest
from behave import given, when, then


from avatar_rules import get_category_objects, get_category_id_from_label



@given(u'the kano-profile-customise app is loaded')
def create_app_step(ctx):
    from kano_avatar_gui.customise import show_wardrobe
    ctx.win = show_wardrobe()


def after_feature(ctx, feature):
    if ctx.win:
        ctx.win.destroy()


@when(u'the app shows')
def refresh_gui(ctx):
    from gi.repository import Gtk
    while Gtk.events_pending():
        Gtk.main_iteration_do(blocking=True)


@then(u'the "{category}" menu is shown')
def shown_menu_step(ctx, category):
    expected_cat_id = get_category_id_from_label(category)

    char = ctx.win.char_edit
    char_menu = char._menu

    # Simple check
    assert char_menu.get_selected_category() == expected_cat_id

    # Popup menu check
    for cat, menu in char_menu.menus.iteritems():
        popup = menu['pop_up']
        if cat != expected_cat_id:
            assert not popup.get_visible()
            continue

        assert popup.get_visible()

        displayed_items = popup._items.keys()
        displayed_items.sort()

        cat_objs = get_category_objects(expected_cat_id)
        obj_ids = [obj.get('item_id') for obj in cat_objs]
        obj_ids.sort()

        assert displayed_items == obj_ids
