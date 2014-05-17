#!/usr/bin/env python

# item_group.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# This contains the interactions between items - useful for the info screen


class ItemGroup():
    def __init__(self, items):
        self.items = items

        # For now - but this should probably be None or set by setter externally
        self.visible = items[0]

        # Only valid if itams are equipable
        # self.equipped is None or an item
        self.equipped = None

    def get_number_of_items(self):
        return len(self.items)

    def get_item_by_index(self, index):
        return self.items[index]

    def set_visible_item(self, item):
        for i in self.items:
            i.set_visible(False)
        self.visible = item
        item.set_visible(True)

    def get_visible_item(self):
        return self.visible

    def unequip_all(self):
        for item in self.items:
            if item.equipable:
                item.set_equipped(False)
                self.equipped = None

    def get_equipped_item(self):
        return self.equipped

    def set_equipped_item(self, item):
        self.unequip_all()
        if item is not None and item.equipable:
            for i in self.items:
                i.set_equipped(False)
            self.equipped = item
            item.set_equipped(True)

    def get_item_from_tuple(self, category, subcategory, name):
        for item in self.items:
            if item.category == category and item.subcategory == subcategory and item.name == name:
                return item

    def get_color(self):
        return self.visible.get_color()

    # move = -1 will select previous item
    # move = 1 will select next item
    def go_to(self, move):
        index = self.items.index(self.visible)
        index = index + move
        if index >= len(self.items):
            index = 0
        elif index < 0:
            index = len(self.items) - 1
        self.set_visible_item(self.items[index])
