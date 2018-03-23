# utils.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utility function used during testing.


import itertools


def all_combinations(items):
    """Generate all combinations of items from a list.

    Args:
        items (list): A list containing any objects inside.

    Returns:
        itertools.chain: An iterable object with tuples containing all
            combinations of items from the list including the empty one.

    Example:
        my_list = [1, 2, 3]

        for combination in all_combinations(my_list):
            print combination

        Output:
            ()
            (1,)
            (2,)
            (3,)
            (1, 2)
            (1, 3)
            (2, 3)
            (1, 2, 3)
    """
    return itertools.chain.from_iterable(
        itertools.combinations(items, length)
        for length in xrange(0, len(items) + 1)
    )
