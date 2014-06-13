#!/usr/bin/env python

# swags.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Controls UI of swag screen

import kano_profile_gui.selection_table_components.table_template as table_template

img_width = 50
swag_ui = None


# _home_button is the avatar face on the home button
# TODO: find a nicer way to do this
def activate(_win, _box, _home_button):
    global swag_ui

    headers = ["avatars", "environments"]
    equipable = True

    if swag_ui is None:
        swag_ui = table_template.TableTemplate(headers, equipable, _home_button)

    swag_ui.leave_info_screen()
    _box.pack_start(swag_ui.container, False, False, 0)

    _win.show_all()

    # Hide all labels on images
    swag_ui.hide_labels()
