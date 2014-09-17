#!/usr/bin/env python

# info_text.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Info display next to image on selected screen

from gi.repository import Gtk, Gdk
from kano.gtk3.buttons import KanoButton


class InfoTextUi():
    def __init__(self, visible_item):

        # self.equip decides whether we include an Equip button on the screen
        self.visible_item = visible_item
        self.equip = visible_item.equipable
        self.width = 274
        self.height = 448
        top_padding = 20
        bottom_padding = 20
        right_padding = 20
        left_padding = 20

        self.heading = Gtk.Label(visible_item.title)
        self.heading.set_alignment(0, 0.5)
        self.heading.set_line_wrap(True)
        self.heading.get_style_context().add_class("info_heading")

        self.paragraph = Gtk.TextView()
        self.paragraph.set_wrap_mode(Gtk.WrapMode.WORD)
        self.paragraph.set_editable(False)
        self.paragraph.get_buffer().set_text(visible_item.get_description())
        self.paragraph.get_style_context().add_class("info_paragraph")
        self.paragraph.set_margin_top(20)
        self.paragraph.set_margin_bottom(30)

        color_str = visible_item.get_color().to_string()
        transparent = self.change_opacity_of_color(color_str, 0.0)
        transparent_background = Gdk.RGBA()
        transparent_background.parse(transparent)
        pale = self.change_opacity_of_color(color_str, 0.3)
        pale_background = Gdk.RGBA()
        pale_background.parse(pale)

        self.heading.override_background_color(Gtk.StateFlags.NORMAL, transparent_background)
        self.paragraph.override_background_color(Gtk.StateFlags.NORMAL, transparent_background)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.pack_start(self.heading, False, False, 5)
        self.box.pack_start(self.paragraph, False, False, 0)
        self.box.set_size_request(self.width - left_padding - right_padding, self.height - top_padding - bottom_padding)

        self.back_button = KanoButton("BACK")
        # Puts the button into a Gtk.Box, to stop it filling up the container
        self.back_button.pack()

        self.equip_button = None

        if self.equip:
            self.equip_button = KanoButton("EQUIP")
            self.equip_button.pack()
            self.box.pack_start(self.equip_button.box, False, False, 3)

        self.box.pack_start(self.back_button.box, False, False, 3)

        self.align = Gtk.Alignment(xalign=0, yalign=0)
        self.align.set_padding(top_padding, bottom_padding, left_padding, right_padding)
        self.align.add(self.box)

        self.background = Gtk.EventBox()
        self.background.add(self.align)
        self.background.override_background_color(Gtk.StateFlags.NORMAL, pale_background)

    def change_opacity_of_color(self, color_str, opacity):
        # Make colour less opaque
        color_str = color_str[:len(color_str) - 1]
        first_part = color_str[:3]
        second_part = color_str[3:]
        color_str = first_part + 'a' + second_part + ',' + str(opacity) + ')'
        return color_str

    def refresh(self, heading, info, color):
        self.heading.set_text(heading)
        self.paragraph.get_buffer().set_text(info)
        self.refresh_background(color)

    def refresh_background(self, color):
        color_str = color.to_string()
        pale = self.change_opacity_of_color(color_str, 0.3)
        pale_background = Gdk.RGBA()
        pale_background.parse(pale)
        self.background.override_background_color(Gtk.StateFlags.NORMAL, pale_background)

    def set_equip_sensitive(self, bool_value):
        if self.equip:
            self.equip_button.set_sensitive(not bool_value)
