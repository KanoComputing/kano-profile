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
        self.equipped = items[0].get_equipped()

    def get_number_of_items(self):
        return len(self.items)

    def get_item_by_index(self, index):
        return self.items[index]

    def set_visible(self, item):
        for i in self.items:
            i.set_visible(False)
        self.visible = item
        item.set_visible(True)

    def get_visible(self):
        return self.visible

    def set_equipped_item(self, item):
        if item.get_equipable():
            for i in self.items:
                i.set_equipped(False)
            self.equipped = item
            item.set_equipped(True)

    def unequip_all(self):
        for item in self.items:
            if item.get_equipable():
                item.set_equipped(False)

    def get_equipped(self):
        return self.get_visible().equipped

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
        self.set_visible(self.items[index])
